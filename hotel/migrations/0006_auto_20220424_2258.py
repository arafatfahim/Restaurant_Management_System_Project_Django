# Generated by Django 3.2 on 2022-04-24 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0005_auto_20220302_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='referal_code',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='food_items',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]