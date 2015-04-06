# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20150405_1636'),
        ('members', '0004_auto_20150405_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stripe_id', models.TextField(null=True, blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('currency', models.CharField(max_length=3, default='usd')),
                ('state', models.PositiveSmallIntegerField(choices=[(0, 'Unprocessed'), (1, 'Submitted'), (2, 'Successful'), (3, 'Failed')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stripe_id', models.TextField()),
                ('member', models.ForeignKey(to='members.Member')),
            ],
        ),
        migrations.AddField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(to='payments_stripe.Customer'),
        ),
        migrations.AddField(
            model_name='charge',
            name='payment_method',
            field=models.ForeignKey(to='accounting.PaymentMethod'),
        ),
    ]
