# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 20:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shareWear', '0012_profile_likes_outfit'),
    ]

    operations = [
        migrations.CreateModel(
            name='profile_follows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_following', to='shareWear.profile')),
                ('profile_main', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_main', to='shareWear.profile')),
            ],
        ),
    ]