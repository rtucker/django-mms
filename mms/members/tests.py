from django.test import TestCase
from members.models import Member
from datetime import date


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
