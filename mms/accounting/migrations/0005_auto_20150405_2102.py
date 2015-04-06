# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_ledgerentry_effective_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ledgerentry',
            options={'verbose_name': 'ledger entry', 'verbose_name_plural': 'ledger entries'},
        ),
    ]
