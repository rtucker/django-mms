# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledgeraccount',
            name='account_type',
            field=models.SmallIntegerField(choices=[(-1, 'Asset'), (-2, 'Expense'), (0, 'Equity'), (1, 'Liability'), (2, 'Income')]),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='api',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Stripe'), (2, 'Stripe (Bitcoin)'), (3, 'PayPal')], default=0),
        ),
    ]
