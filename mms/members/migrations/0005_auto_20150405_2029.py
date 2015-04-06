# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_auto_20150405_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 6, 0, 29, 8, 317834, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='last_billed',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
