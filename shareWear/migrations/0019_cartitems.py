# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-17 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shareWear', '0018_auto_20170416_0104'),
    ]

    operations = [
        migrations.CreateModel(
            name='cartItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clothing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shareWear.clothing')),
                ('outfit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shareWear.outfit')),
            ],
        ),
    ]