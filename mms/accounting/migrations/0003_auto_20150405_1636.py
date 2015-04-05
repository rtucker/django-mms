# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20150405_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledgeraccount',
            name='gnucash_account',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='api',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Stripe'), (2, 'Stripe Bitcoin'), (3, 'PayPal')], default=0),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='fee_account',
            field=models.ForeignKey(blank=True, to='accounting.LedgerAccount', related_name='+', null=True),
        ),
    ]
