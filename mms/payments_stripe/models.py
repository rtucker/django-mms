from django.db import models
from django.conf import settings

from members.models import Member
from accounting.models import PaymentMethod, LedgerEntry

from decimal import Decimal
import stripe

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
currency = getattr(settings, "DEFAULT_CURRENCY_CODE", None)


class CustomerManager(models.Manager):
    def create_customer(self, member):
        # TODO: error checking
        # TODO: search for existing user
        obj = stripe.Customer.create(
            description="%s via django-mms" % member.name,
            email=member.email,
        )

        cust = self.create(member=member, stripe_id=obj.id)

        return cust


class Customer(models.Model):
    member = models.OneToOneField(Member)
    stripe_id = models.CharField(max_length=200)

    objects = CustomerManager()

    def __str__(self):
        return "%s - %s" % (self.member.name, self.stripe_id)

    def get_stripe_object(self):
        return stripe.Customer.retrieve(self.stripe_id)
    stripe_object = property(get_stripe_object)

    # Card management
    def get_cards(self):
        result = []
        has_more = True
        starting_after = None
        while has_more:
            response = self.stripe_object.sources.all(
                object='card',
                starting_after=starting_after)
            has_more = response.has_more
            if len(response.data) > 0:
                starting_after = response.data[-1:][0].id
            result.extend(response.data)
        return result
    cards = property(get_cards)

    def get_card(self, card_id):
        return self.stripe_object.sources.retrieve(card_id)

    def get_default_card(self):
        ds = self.stripe_object.default_source
        if ds is not None:
            return self.get_card(ds)
        return None
    default_card = property(get_default_card)

    def add_card(self, token, default=True):
        if default:
            cust = self.stripe_object
            cust.source = token
            cust.save()
        else:
            self.stripe_object.sources.create(card=token)

    def delete_card(self, card_id):
        return self.get_card(card_id).delete()


class ChargeManager(models.Manager):
    def create_charge(self, customer, amount, method, description,
                      descriptor=None):
        """Expects amount in Decimal (3.50)"""
        obj = stripe.Charge.create(
            amount=int(amount*100),
            currency=currency,
            customer=customer.stripe_id,
            description=description,
            statement_descriptor=descriptor,
        )

        chrg = self.create(
            customer=customer,
            payment_method=method,
            stripe_id=obj.id,
            amount=amount,
            currency=currency,
            state=Charge.STATE_SENT,
        )

        chrg.state_update()

        return chrg


class Charge(models.Model):
    """A charge against a customer's card.

    Responsible for creating LedgerEntries for:
        - Debit payment_method.fee_account for transaction fee
        - Debit payment_method.revenue_account for remainder
        - Credit customer.member.account for full amount
    """

    STATE_INIT = 0
    STATE_SENT = 1
    STATE_SUCCESSFUL = 2
    STATE_FAILED = 3
    STATE_COMPLETED = 4
    STATE_CHOICES = (
        (STATE_INIT, "Unprocessed"),
        (STATE_SENT, "Submitted"),
        (STATE_SUCCESSFUL, "Successful"),
        (STATE_FAILED, "Failed"),
        (STATE_COMPLETED, "Completed"),
    )

    created_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer)
    payment_method = models.ForeignKey(PaymentMethod)
    stripe_id = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3,
                                default=currency)
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES,
                                             default=STATE_INIT)
    transaction = models.ManyToManyField(LedgerEntry)

    objects = ChargeManager()

    def __str__(self):
        if self.stripe_id is not None and len(self.stripe_id) > 0:
            return "%.2f from %s (%s, %s)" % (
                self.amount, self.customer, self.stripe_id,
                self.get_state_display())
        else:
            return "%.2f from %s (%s)" % (self.amount, self.customer,
                                          self.get_state_display())

    def get_stripe_object(self):
        return stripe.Charge.retrieve(self.stripe_id)
    stripe_object = property(get_stripe_object)

    def get_stripe_balance_transactions(self):
        result = []
        has_more = True
        starting_after = None
        while has_more:
            response = stripe.BalanceTransaction.all(
                source=self.stripe_id,
                starting_after=starting_after)
            has_more = response.has_more
            if len(response.data) > 0:
                starting_after = response.data[-1:][0].id
            result.extend(response.data)
        return result
    stripe_balance_transactions = property(get_stripe_balance_transactions)

    def get_transaction_amounts(self):
        for bt in self.stripe_balance_transactions:
            yield {'amount': Decimal(bt.amount)/100,
                   'fee':    Decimal(bt.fee)/100,
                   'net':    Decimal(bt.net)/100}
    transaction_amounts = property(get_transaction_amounts)

    def state_update(self):
        if self.state == self.STATE_SENT:
            # transaction has been sent, but is in purgatory
            if self.stripe_object.status == 'succeeded':
                self.state = self.STATE_SUCCESSFUL
                self.save()
            if self.stripe_object.status == 'failed':
                self.state = self.STATE_FAILED
                self.save()

        if self.state == self.STATE_SUCCESSFUL:
            # transaction was successful, update our ledger
            for amts in self.transaction_amounts:
                # Create ledger entry for full amount
                le_gross = LedgerEntry.objects.create(
                    debit_account=self.payment_method.revenue_account,
                    credit_account=self.customer.member.account,
                    amount=amts['amount'],
                    details='%s txn %s' % (self.payment_method,
                                           self.stripe_id),
                )
                self.transaction.add(le_gross)

                # Create ledger entry for fee amount
                le_fee = LedgerEntry.objects.create(
                    debit_account=self.payment_method.fee_account,
                    credit_account=self.payment_method.revenue_account,
                    amount=amts['fee'],
                    details='%s txn %s fees' % (self.payment_method,
                                                self.stripe_id),
                )
                self.transaction.add(le_fee)

            self.state = self.STATE_COMPLETED
            self.save()
