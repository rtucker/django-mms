# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LedgerAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gnucash_account', models.TextField()),
                ('account_type', models.SmallIntegerField(choices=[(-1, b'Asset'), (-2, b'Expense'), (0, b'Equity'), (1, b'Liability'), (2, b'Income')])),
            ],
        ),
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('details', models.TextField()),
                ('credit_account', models.ForeignKey(related_name='credit_transactions', to='accounting.LedgerAccount')),
                ('debit_account', models.ForeignKey(related_name='debit_transactions', to='accounting.LedgerAccount')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('is_recurring', models.BooleanField()),
                ('is_automated', models.BooleanField()),
                ('api', models.PositiveSmallIntegerField(default=0, choices=[(0, b'None'), (1, b'Stripe'), (2, b'Stripe (Bitcoin)'), (3, b'PayPal')])),
                ('fee_account', models.ForeignKey(related_name='+', to='accounting.LedgerAccount')),
                ('revenue_account', models.ForeignKey(related_name='+', to='accounting.LedgerAccount')),
            ],
        ),
    ]
