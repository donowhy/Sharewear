# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 23:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareWear', '0003_auto_20170326_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clothing',
            name='price',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
