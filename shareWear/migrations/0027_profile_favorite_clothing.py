# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-08 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareWear', '0026_clothing_cloth_sub_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite_clothing',
            field=models.ManyToManyField(to='shareWear.clothing'),
        ),
    ]