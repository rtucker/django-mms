# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments_stripe', '0002_auto_20150405_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='stripe_id',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='stripe_id',
            field=models.CharField(max_length=200),
        ),
    ]
