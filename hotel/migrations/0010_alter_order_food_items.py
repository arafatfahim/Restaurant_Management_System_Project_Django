# Generated by Django 3.2 on 2022-04-23 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0009_order_food_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='food_items',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]