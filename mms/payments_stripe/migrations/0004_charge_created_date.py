# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('payments_stripe', '0003_auto_20150405_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 5, 22, 34, 37, 656482, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
