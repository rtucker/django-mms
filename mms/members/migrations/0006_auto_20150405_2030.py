# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20150405_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_billed',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
