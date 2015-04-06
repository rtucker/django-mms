# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20150405_1636'),
        ('payments_stripe', '0004_charge_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='transaction',
            field=models.ManyToManyField(to='accounting.LedgerEntry'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Unprocessed'), (1, 'Submitted'), (2, 'Successful'), (3, 'Failed'), (4, 'Completed')], default=0),
        ),
    ]
