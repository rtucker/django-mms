# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150405_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='membership',
            field=models.ForeignKey(null=True, to='members.MembershipLevel'),
        ),
        migrations.AlterField(
            model_name='member',
            name='account',
            field=models.OneToOneField(to='accounting.LedgerAccount', null=True),
        ),
        migrations.AlterField(
            model_name='membershiplevel',
            name='per',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'month'), (3, 'quarter'), (12, 'year')]),
        ),
    ]
