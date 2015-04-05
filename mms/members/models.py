from django.db import models

from accounting.models import LedgerAccount

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

class Member(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    account = models.OneToOneField(LedgerAccount, limit_choices_to={'account_type': LedgerAccount.TYPE_LIABILITY}, blank=True, null=True)
    membership = models.ForeignKey(MembershipLevel, blank=True, null=True)

    def __str__(self):
        if self.membership is not None:
            return "%s (%s)" % (self.name, self.membership)
        return "%s" % self.name