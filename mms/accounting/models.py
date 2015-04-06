from django.db import models
from django.db.models import Sum
from django.utils import timezone

from decimal import Decimal

class LedgerAccount(models.Model):
    """A particular account in the accounting ledger.

    All transactions must have a left side (debit) and a right side (credit),
    and they must add up to zero.
    """
    # Hint:
    # Type < 0: debit increases, credit decreases (normal balance = debit)
    # Type >= 0: debit decreases, credit increases (normal balance = credit)
    TYPE_ASSET = -1
    TYPE_EXPENSE = -2
    TYPE_EQUITY = 0
    TYPE_LIABILITY = 1
    TYPE_INCOME = 2
    TYPE_CHOICES = (
        (TYPE_ASSET, 'Asset'),
        (TYPE_EXPENSE, 'Expense'),
        (TYPE_EQUITY, 'Equity'),
        (TYPE_LIABILITY, 'Liability'),
        (TYPE_INCOME, 'Income'),
    )
    gnucash_account = models.TextField(blank=True)
    account_type = models.SmallIntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        if self.gnucash_account is not None and len(self.gnucash_account) > 0:
            return "%s account '%s'" % (self.get_account_type_display(), self.gnucash_account)
        else:
            try:
                return "%s account for member %s" % (self.get_account_type_display(), self.member.name)
            except models.fields.related.RelatedObjectDoesNotExist:
                return "%s account %d" % (self.get_account_type_display(), self.pk)

    def get_credits(self):
        the_sum = self.credit_transactions.all().aggregate(Sum('amount'))['amount__sum']
        if the_sum is None:
            the_sum = Decimal('0.00')
        return the_sum
    credits = property(get_credits)

    def get_debits(self):
        the_sum = self.debit_transactions.all().aggregate(Sum('amount'))['amount__sum']
        if the_sum is None:
            the_sum = Decimal('0.00')
        return the_sum
    debits = property(get_debits)

    def get_balance(self):
        return self.debits - self.credits
    balance = property(get_balance)

    def get_account_balance(self):
        if self.account_type < 0:
            return self.debits - self.credits
        else:
            return self.credits - self.debits
    account_balance = property(get_account_balance)

class LedgerEntry(models.Model):
    """A financial transaction, implemented as a transfer between two
    LedgerAccounts.
    """
    effective_date = models.DateField(default=timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    debit_account = models.ForeignKey(LedgerAccount, related_name="debit_transactions")
    credit_account = models.ForeignKey(LedgerAccount, related_name="credit_transactions")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    details = models.TextField()

    class Meta:
        verbose_name = 'ledger entry'
        verbose_name_plural = 'ledger entries'

    def __str__(self):
        return "Amount %.2f (debit acct %s, credit acct %s, description %s)" % (
            self.amount, self.debit_account, self.credit_account, self.details)

class PaymentMethod(models.Model):
    API_NONE = 0
    API_STRIPEIO = 1
    API_STRIPEIO_BITCOIN = 2
    API_PAYPAL = 3
    API_CHOICES = (
        (API_NONE, 'None'),
        (API_STRIPEIO, 'Stripe'),
        (API_STRIPEIO_BITCOIN, 'Stripe Bitcoin'),
        (API_PAYPAL, 'PayPal'),
    )
    name = models.CharField(max_length=200)
    is_recurring = models.BooleanField()
    is_automated = models.BooleanField()
    api = models.PositiveSmallIntegerField(choices=API_CHOICES, default=API_NONE)
    revenue_account = models.ForeignKey(LedgerAccount, related_name="+", limit_choices_to={'account_type': LedgerAccount.TYPE_ASSET})
    fee_account = models.ForeignKey(LedgerAccount, related_name="+", limit_choices_to={'account_type': LedgerAccount.TYPE_EXPENSE}, blank=True, null=True)

    def __str__(self):
        if self.api is not self.API_NONE:
            return "%s (via %s)" % (self.name, self.get_api_display())
        else:
            return "%s" % self.name
