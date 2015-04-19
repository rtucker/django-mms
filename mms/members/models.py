from django.db import models
from django.utils import timezone

from accounting.models import LedgerAccount, LedgerEntry


class MembershipLevel(models.Model):
    """Descriptor for membership costs and privileges.

    :param name: Name of membership level.
    :param cost: Cost of this membership level.
    :param per: Billing interval for this level.
    :param account:
        :py:class:`LedgerAccount` for income from this membership level.
        Must be TYPE_INCOME.

    The following grant privileges to members subscribed to this plan:

    :param has_keyfob: Does the user get 24x7 access via keyfob?
    :param has_room_key: Does the member get access to a locked room?
    :param has_voting: Does the member get a vote?
    :param has_powertool_access: Can the member use power tools?
    """
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
    per = models.PositiveSmallIntegerField(choices=PER_CHOICES,
                                           default=PER_MONTH)
    has_keyfob = models.BooleanField()
    has_room_key = models.BooleanField()
    has_voting = models.BooleanField()
    has_powertool_access = models.BooleanField()
    account = models.ForeignKey(
        LedgerAccount,
        limit_choices_to={'account_type': LedgerAccount.TYPE_INCOME})

    def __str__(self):
        return "%s ($%.2f/%s)" % (self.name, self.cost, self.get_per_display())


class Member(models.Model):
    """A member of our august institution.

    :param name: Name of member.
    :param email: E-mail address for member.
    :param created:
        :class:`django.db.models.DateTimeField` with creation time of this
        entry.  Immutable.
    :param account:
        :py:class:`LedgerAccount` for member-specific balance.  Must be
        TYPE_LIABILITY.
    :param membership: :py:class:`MembershipLevel` for this member.
    :param last_billed:
        :class:`django.db.models.DateField` storing the last date this member
        was billed.  Defaults to :func:`django.utils.timezone.now`.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    account = models.OneToOneField(
        LedgerAccount,
        limit_choices_to={'account_type': LedgerAccount.TYPE_LIABILITY},
        blank=True, null=True)
    membership = models.ForeignKey(MembershipLevel, blank=True, null=True)
    last_billed = models.DateField(default=timezone.now)

    def __str__(self):
        if self.membership is not None:
            return "%s (%s)" % (self.name, self.membership)
        return "%s" % self.name

    @staticmethod
    def add_n_months(original, months):
        """Adds (or subtracts) a number of *months* from the *original* date.

        Tries to get as close to "the *n*th of the month" as possible, but in
        the event that date doesn't exist (e.g. February 30th), it will choose
        a close date.  For example, 1 month after January 31, 2015 will be
        February 28, 2015.
        """
        year = original.year
        month = original.month
        day = original.day

        month += months

        while True:
            while day < 1:
                day += 31
                month -= 1

            while month < 1:
                year -= 1
                month += 12

            while month > 12:
                year += 1
                month -= 12

            try:
                new = original.replace(year=year, month=month, day=day)
                break
            except ValueError:
                # day is most likely out of range (e.g. February 30)
                day -= 1

        return new

    def get_next_bill_date(self):
        if self.membership is not None:
            return self.add_n_months(self.last_billed, self.membership.per)
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
                effective_date=self.next_bill_date,
                debit_account=self.account,
                credit_account=self.membership.account,
                amount=self.membership.cost,
                details="%s, 1 %s (%s to %s)" % (
                    self.membership.name,
                    self.membership.get_per_display(),
                    self.next_bill_date,
                    self.add_n_months(self.next_bill_date, self.membership.per)
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
