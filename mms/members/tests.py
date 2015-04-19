from django.test import TestCase
from accounting.models import LedgerAccount
from members.models import Member, MembershipLevel
from datetime import date
from decimal import Decimal


def dttm_to_date(v):
    return date(v.year, v.month, v.day)


class MemberTestCase(TestCase):
    def setUp(self):
        self.ml_full_monthly = MembershipLevel.objects.create(
            name="Monthly Full",
            cost="50.00",
            per=MembershipLevel.PER_MONTH,
            has_keyfob=True,
            has_room_key=False,
            has_voting=True,
            has_powertool_access=True,
            account=LedgerAccount.objects.create(
                gnucash_account="Income:Member Dues:Full",
                account_type=LedgerAccount.TYPE_INCOME,
            ),
        )

        self.ml_full_yearly = MembershipLevel.objects.create(
            name="Yearly Full",
            cost="600.00",
            per=MembershipLevel.PER_YEAR,
            has_keyfob=True,
            has_room_key=False,
            has_voting=True,
            has_powertool_access=True,
            account=LedgerAccount.objects.create(
                gnucash_account="Income:Member Dues:Full",
                account_type=LedgerAccount.TYPE_INCOME,
            ),
        )

        self.member1 = Member.objects.create(
            name="Member 1",
            email="member1@example.com",
            account=LedgerAccount.objects.create(
                gnucash_account="Liability:Member Accounts",
                account_type=LedgerAccount.TYPE_LIABILITY,
            ),
            membership=self.ml_full_monthly,
            last_billed=date(2013, 12, 30),
        )

        self.member2 = Member.objects.create(
            name="Member 2",
            email="member2@example.com",
            account=LedgerAccount.objects.create(
                gnucash_account="Liability:Member Accounts",
                account_type=LedgerAccount.TYPE_LIABILITY,
            ),
            membership=self.ml_full_yearly,
            last_billed=date(2012, 2, 29),
        )

        self.member3 = Member.objects.create(
            name="Member 3",
            email="member3@example.com",
            account=LedgerAccount.objects.create(
                gnucash_account="Liability:Member Accounts",
                account_type=LedgerAccount.TYPE_LIABILITY,
            ),
            membership=None,
            last_billed=date(2011, 1, 1),
        )

        self.member4 = Member.objects.create(
            name="Member 4",
            email="member4@example.com",
            account=None,
            membership=None,
            last_billed=date(2011, 1, 1),
        )

    def test_next_bill_date(self):
        self.assertEqual(dttm_to_date(self.member1.next_bill_date),
                         date(2014, 1, 30))
        self.assertEqual(dttm_to_date(self.member2.next_bill_date),
                         date(2013, 2, 28))
        self.assertEqual(self.member3.next_bill_date, None)
        self.assertEqual(self.member4.next_bill_date, None)

    def test_billing_up_to_date(self):
        self.assertFalse(self.member1.billing_up_to_date)
        self.assertFalse(self.member2.billing_up_to_date)
        self.assertEqual(self.member3.billing_up_to_date, None)
        self.assertEqual(self.member4.billing_up_to_date, None)

    def test_do_regular_billing_member1(self):
        self.assertEqual(self.member1.balance, Decimal('0.00'))
        self.assertNotEqual(self.member1.do_regular_billing(), None)
        self.assertEqual(dttm_to_date(self.member1.next_bill_date),
                         date(2014, 2, 28))
        self.assertEqual(self.member1.balance, Decimal('-50.00'))

    def test_do_regular_billing_member2(self):
        self.assertEqual(self.member2.balance, Decimal('0.00'))
        self.assertNotEqual(self.member2.do_regular_billing(), None)
        self.assertEqual(dttm_to_date(self.member2.next_bill_date),
                         date(2014, 2, 28))
        self.assertEqual(self.member2.balance, Decimal('-600.00'))

    def test_do_regular_billing_member3(self):
        self.assertEqual(self.member3.balance, Decimal('0.00'))
        self.assertEqual(self.member3.do_regular_billing(), None)
        self.assertEqual(self.member3.balance, Decimal('0.00'))

    def test_do_regular_billing_member4(self):
        self.assertEqual(self.member4.balance, None)
        self.assertEqual(self.member4.do_regular_billing(), None)
        self.assertEqual(self.member4.balance, None)

    def test_do_regular_billing_member1_loop(self):
        self.assertEqual(self.member1.balance, Decimal('0.00'))
        count = 0
        while True:
            result = self.member1.do_regular_billing()
            if result is None:
                break
            count += 1
        self.assertGreater(count, 0)
        self.assertEqual(self.member1.balance, Decimal('-50.00')*count)
        self.assertGreater(self.member1.next_bill_date, date.today())

    def test_do_regular_billing_member2_loop(self):
        self.assertEqual(self.member2.balance, Decimal('0.00'))
        count = 0
        while True:
            result = self.member2.do_regular_billing()
            if result is None:
                break
            count += 1
        self.assertGreater(count, 0)
        self.assertEqual(self.member2.balance, Decimal('-600.00')*count)
        self.assertGreater(self.member2.next_bill_date, date.today())


class MemberAddNMonthsTestCase(TestCase):
    def test_jan1_plus_1(self):
        # 1 month after January 1 is February 1
        self.assertEqual(Member.add_n_months(date(2015, 1, 1), 1),
                         date(2015, 2, 1))

    def test_jan30_plus_1(self):
        # 1 month after January 30 is February 28
        self.assertEqual(Member.add_n_months(date(2015, 1, 30), 1),
                         date(2015, 2, 28))

    def test_jan1_plus_2(self):
        # 2 months after January 1 is March 1
        self.assertEqual(Member.add_n_months(date(2015, 1, 1), 2),
                         date(2015, 3, 1))

    def test_dec1_plus_2(self):
        # 2 months after December 1 is February 1
        self.assertEqual(Member.add_n_months(date(2014, 12, 1), 2),
                         date(2015, 2, 1))

    def test_dec30_plus_2(self):
        # 2 months after December 30 is February 28
        self.assertEqual(Member.add_n_months(date(2014, 12, 30), 2),
                         date(2015, 2, 28))
        # or February 29
        self.assertEqual(Member.add_n_months(date(2015, 12, 30), 2),
                         date(2016, 2, 29))

    def test_jan1_plus_12(self):
        # 12 months after January 1 is January 1 next year
        self.assertEqual(Member.add_n_months(date(2015, 1, 1), 12),
                         date(2016, 1, 1))

    def test_jan1_minus_1(self):
        # 1 month before January 1 is December 1
        self.assertEqual(Member.add_n_months(date(2015, 1, 1), -1),
                         date(2014, 12, 1))

    def test_dec31_minus_1(self):
        # 1 month before December 31 is November 30
        self.assertEqual(Member.add_n_months(date(2015, 12, 31), -1),
                         date(2015, 11, 30))

    def test_march1_minus_1(self):
        # 1 month before March 1 is February 1
        self.assertEqual(Member.add_n_months(date(2015, 3, 1), -1),
                         date(2015, 2, 1))

    def test_march30_minus_1(self):
        # 1 month before March 30 is February 28
        self.assertEqual(Member.add_n_months(date(2015, 3, 30), -1),
                         date(2015, 2, 28))
        # or February 29
        self.assertEqual(Member.add_n_months(date(2016, 3, 30), -1),
                         date(2016, 2, 29))
