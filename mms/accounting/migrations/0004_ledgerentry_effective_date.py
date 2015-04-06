# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20150405_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='ledgerentry',
            name='effective_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
