# Generated by Django 3.2 on 2022-04-24 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0014_order_food_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='food_items',
            field=models.TextField(null=True),
        ),
    ]
