# Generated by Django 3.0.8 on 2021-02-11 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_descr', models.CharField(max_length=100)),
                ('full_descr', models.CharField(max_length=500)),
                ('views_cnt', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.CharField(max_length=500, null=True)),
                ('price', models.IntegerField(default=0)),
                ('tag', models.ManyToManyField(to='goods_service.Tag')),
            ],
        ),
    ]