# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20150405_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='account',
            field=models.OneToOneField(blank=True, to='accounting.LedgerAccount', null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='membership',
            field=models.ForeignKey(blank=True, to='members.MembershipLevel', null=True),
        ),
    ]
