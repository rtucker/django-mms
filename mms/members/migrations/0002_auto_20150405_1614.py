# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiplevel',
            name='per',
            field=models.PositiveSmallIntegerField(choices=[(1, '/month'), (3, '/quarter'), (12, '/year')], default=1),
        ),
    ]
