# Generated by Django 3.2 on 2022-04-23 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0008_remove_order_food_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='food_items',
            field=models.TextField(blank=True, null=True),
        ),
    ]