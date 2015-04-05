from django.db import models

# Create your models here.

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
    gnucash_account = models.TextField()
    account_type = models.SmallIntegerField(choices=TYPE_CHOICES)

class LedgerEntry(models.Model):
    """A financial transaction, implemented as a transfer between two
    LedgerAccounts.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    debit_account = models.ForeignKey(LedgerAccount, related_name="debit_transactions", limit_choices_to={'account_type__lt': 0})
    credit_account = models.ForeignKey(LedgerAccount, related_name="credit_transactions", limit_choices_to={'account_type__gte': 0})
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    details = models.TextField()

class PaymentMethod(models.Model):
    API_NONE = 0
    API_STRIPEIO = 1
    API_STRIPEIO_BITCOIN = 2
    API_PAYPAL = 3
    API_CHOICES = (
        (API_NONE, 'None'),
        (API_STRIPEIO, 'Stripe'),
        (API_STRIPEIO_BITCOIN, 'Stripe (Bitcoin)'),
        (API_PAYPAL, 'PayPal'),
    )
    name = models.CharField(max_length=200)
    is_recurring = models.BooleanField()
    is_automated = models.BooleanField()
    api = models.PositiveSmallIntegerField(choices=API_CHOICES, default=API_NONE)
    revenue_account = models.ForeignKey(LedgerAccount, related_name="+", limit_choices_to={'account_type': LedgerAccount.TYPE_ASSET})
    fee_account = models.ForeignKey(LedgerAccount, related_name="+", limit_choices_to={'account_type': LedgerAccount.TYPE_EXPENSE})