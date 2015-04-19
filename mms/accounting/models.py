from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone

from decimal import Decimal


class LedgerAccount(models.Model):
    """A particular account in the accounting ledger system.

    All transactions must have a left side (debit) and a right side (credit),
    and they must add up to zero.

    This implements the double-entry bookkeeping system.  More background
    information is available in the Wikipedia:

    https://en.wikipedia.org/wiki/Double-entry_bookkeeping_system

    The normal balance for each account is determined by the
    :py:attr:`account_type`, in particular whether the integer value
    is less than zero:

       +-----------+-----+---------+
       | Type      | Int | Balance |
       +===========+=====+=========+
       | Expense   |  -2 | debit   |
       +-----------+-----+---------+
       | Asset     |  -1 | debit   |
       +-----------+-----+---------+
       | Equity    |   0 | credit  |
       +-----------+-----+---------+
       | Liability |   1 | credit  |
       +-----------+-----+---------+
       | Income    |   2 | credit  |
       +-----------+-----+---------+

    :param gnucash_account:
        Corresponding Gnucash account.  Used for data exchange with the core
        accounting system.
    :param account_type:
        Type of account, based on double-entry bookkeeping principles.  This
        is from *our* perspective: an account where a member deposits money
        would be a Liability account.
    """
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
            return "%s account '%s'" % (self.get_account_type_display(),
                                        self.gnucash_account)
        else:
            try:
                return "%s account for member %s" % (
                    self.get_account_type_display(), self.member.name)
            except models.fields.related.RelatedObjectDoesNotExist:
                return "%s account %d" % (self.get_account_type_display(),
                                          self.pk)

    def _get_credits(self):
        """The sum of all credit transactions on this account.

        >>> acct.credits
        Decimal('42.00')
        """
        agg = self.credit_transactions.all().aggregate(Sum('amount'))
        the_sum = agg['amount__sum']
        if the_sum is None:
            the_sum = Decimal('0.00')
        return the_sum
    credits = property(_get_credits)

    def _get_debits(self):
        """The sum of all debit transactions on this account.

        >>> acct.debits
        Decimal('23.23')
        """
        agg = self.debit_transactions.all().aggregate(Sum('amount'))
        the_sum = agg['amount__sum']
        if the_sum is None:
            the_sum = Decimal('0.00')
        return the_sum
    debits = property(_get_debits)

    def _get_balance(self):
        """The raw balance of debits and credits on this account.  Simply
        put, this returns debits minus credits without any regard for the
        account's normal balance.

        >>> acct.debits
        Decimal('42.00')
        >>> acct.credits
        Decimal('69.00')
        >>> acct.balance
        Decimal('-27.00')

        The summation of balance across all :py:class:`LedgerAccount` will
        (should?) equal *exactly* zero.

        See also: :py:attr:`account_balance`
        """
        return self.debits - self.credits
    balance = property(_get_balance)

    def _get_account_balance(self):
        """The balance of this account.

        Unlike :py:attr:`balance`, this flips the sign for credit accounts
        (e.g. Equity, Liability, Income).

        >>> acct.account_type is TYPE_LIABILITY
        True
        >>> acct.debits
        Decimal('42.00')
        >>> acct.credits
        Decimal('69.00')
        >>> acct.account_balance
        Decimal('-27.00')
        """
        if self.account_type < 0:
            return self.balance
        else:
            return -self.balance
    account_balance = property(_get_account_balance)

    def get_account_transactions(self):
        """Returns a :class:`django.db.models.query.QuerySet` with all
        :py:class:`LedgerEntry` instances referencing this account, whether
        credit or debit.

        Example to print all effective dates and amounts:

        >>> for txn in acct.get_account_transactions():
        ...    print(txn.effective_date, txn.account_net(acct))
        """
        qq = Q(debit_account=self) | Q(credit_account=self)
        txns = LedgerEntry.objects.filter(qq)
        txns = txns.order_by('effective_date', 'created_date')
        return txns


class LedgerEntry(models.Model):
    """A financial transaction, implemented as a transfer between two
    :py:class:`LedgerAccount` instances.

    :param effective_date:
        :class:`django.db.models.DateField` containing the effective date of
        this transaction.  Defaults to :func:`django.utils.timezone.now`.
    :param created_date:
        :class:`django.db.models.DateTimeField` containing the time this
        instance was created.  Immutable.
    :param modified_date:
        :class:`django.db.models.DateTimeField` containing the time this
        instance was last modified.  Immutable.
    :param debit_account:
        :class:`LedgerAccount` for the *left side* of a transaction.
    :param credit_account:
        :class:`LedgerAccount` for the *right side* of a transaction.
    :param amount:
        :class:`django.db.models.DecimalField` with the exact amount of this
        transaction.
    :param details:
        :class:`django.db.models.TextField` free-form description for this
        transaction.
    """
    effective_date = models.DateField(default=timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    debit_account = models.ForeignKey(LedgerAccount,
                                      related_name="debit_transactions")
    credit_account = models.ForeignKey(LedgerAccount,
                                       related_name="credit_transactions")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    details = models.TextField()

    class Meta:
        verbose_name = 'ledger entry'
        verbose_name_plural = 'ledger entries'

    def __str__(self):
        return "Amount %.2f (debit '%s', credit '%s', description '%s')" % (
            self.amount, self.debit_account, self.credit_account, self.details)

    def account_net(self, account):
        """Net effect of this transaction on *account*.

        Equation:
            :py:attr:`amount` = debit - credit

        This method returns :py:attr:`amount` if *account* is the debit
        (left-hand) account and -:py:attr:`amount` if *account* is the credit
        (right-hand) account.

        :param account:
            Account to compute net effect upon.
        """
        amt = 0
        if self.debit_account == account:
            amt += self.amount
        if self.credit_account == account:
            amt -= self.amount
        return amt


class PaymentMethod(models.Model):
    """A valid method of payment, for adding money to a member's account.

    This provides a mapping between a payment processor's API and two
    :py:class:`LedgerAccount` instances, one for revenue and another for
    fees.

    Equation:
        revenue = payment - fees

    where *payment* is the amount credited to the member's account.

    :param name:
        User-friendly description of this payment method.
    :param api:
        The API to use on the back end, selected from :py:attr:`API_CHOICES`
    :param is_recurring:
        True if this method can be used for recurring payments (e.g. Stripe),
        False if it cannot (e.g. Cash).
    :param is_automated:
        True if this method is completely automated from the end user's
        perspective (e.g. Stripe), False if it requires intervention (e.g.
        Cheque).
    :param revenue_account:
        :py:class:`LedgerAccount` for the net transaction amount.  Must
        be TYPE_ASSET.
    :param fee_account:
        :py:class:`LedgerAccount` for the transaction fees.  Must be
        TYPE_EXPENSE.
    """
    API_NONE = 0
    API_STRIPEIO = 1
    API_STRIPEIO_BITCOIN = 2
    API_PAYPAL = 3
    API_CHOICES = (
        (API_NONE, 'None'),
        (API_STRIPEIO, 'Stripe'),
        #(API_STRIPEIO_BITCOIN, 'Stripe Bitcoin'),
        #(API_PAYPAL, 'PayPal'),
    )
    name = models.CharField(max_length=200)
    is_recurring = models.BooleanField()
    is_automated = models.BooleanField()
    api = models.PositiveSmallIntegerField(choices=API_CHOICES,
                                           default=API_NONE)
    revenue_account = models.ForeignKey(
        LedgerAccount, related_name="+",
        limit_choices_to={'account_type': LedgerAccount.TYPE_ASSET})
    fee_account = models.ForeignKey(
        LedgerAccount, related_name="+",
        limit_choices_to={'account_type': LedgerAccount.TYPE_EXPENSE},
        blank=True, null=True)

    def __str__(self):
        if self.api is not self.API_NONE:
            return "%s (via %s)" % (self.name, self.get_api_display())
        else:
            return "%s" % self.name
