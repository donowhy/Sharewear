# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-17 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareWear', '0019_cartitems'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='cart_items',
            field=models.ManyToManyField(to='shareWear.cartItems'),
        ),
    ]
