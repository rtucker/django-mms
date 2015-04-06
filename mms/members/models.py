from django.db import models
from django.utils import timezone

from accounting.models import LedgerAccount, LedgerEntry

class MembershipLevel(models.Model):
    PER_MONTH = 1
    PER_QUARTER = 3
    PER_YEAR = 12
    PER_CHOICES = (
        (PER_MONTH, 'month'),
        (PER_QUARTER, 'quarter'),
        (PER_YEAR, 'year'),
    )
    name = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    per = models.PositiveSmallIntegerField(choices=PER_CHOICES, default=PER_MONTH)
    has_keyfob = models.BooleanField()
    has_room_key = models.BooleanField()
    has_voting = models.BooleanField()
    has_powertool_access = models.BooleanField()
    account = models.ForeignKey(LedgerAccount, limit_choices_to={'account_type': LedgerAccount.TYPE_INCOME})

    def __str__(self):
        return "%s ($%.2f/%s)" % (self.name, self.cost, self.get_per_display())

def add_n_months(original, months):
    year = original.year
    month = original.month

    month += months

    while month > 12:
        year += 1
        month -= 12

    return original.replace(year=year, month=month)

class Member(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    account = models.OneToOneField(LedgerAccount, limit_choices_to={'account_type': LedgerAccount.TYPE_LIABILITY}, blank=True, null=True)
    membership = models.ForeignKey(MembershipLevel, blank=True, null=True)
    last_billed = models.DateField(default=timezone.now)

    def __str__(self):
        if self.membership is not None:
            return "%s (%s)" % (self.name, self.membership)
        return "%s" % self.name

    def get_next_bill_date(self):
        if self.membership is not None:
            return add_n_months(self.last_billed, self.membership.per)
        else:
            return None
    next_bill_date = property(get_next_bill_date)

    def get_billing_up_to_date(self):
        if self.next_bill_date is not None:
            return self.next_bill_date > timezone.now().date()
        else:
            return None
    billing_up_to_date = property(get_billing_up_to_date)

    def do_regular_billing(self):
        # Debit account: member.account
        # Credit account: member.membership.account
        txn = None
        if not self.billing_up_to_date:
            txn = LedgerEntry.objects.create(
                effective_date = self.next_bill_date,
                debit_account = self.account,
                credit_account = self.membership.account,
                amount = self.membership.cost,
                details = "%s, 1 %s (%s to %s)" % (
                    self.membership.name,
                    self.membership.get_per_display(),
                    self.next_bill_date,
                    add_n_months(self.next_bill_date, self.membership.per)
                ),
            )
            self.last_billed = self.next_bill_date
            self.save()
        return txn

    def get_balance(self):
        if self.account is not None:
            return self.account.account_balance
        else:
            return None
    balance = property(get_balance)