# Generated by Django 3.0.8 on 2020-07-18 14:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('goods_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
