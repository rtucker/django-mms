# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments_stripe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='member',
            field=models.OneToOneField(to='members.Member'),
        ),
    ]
