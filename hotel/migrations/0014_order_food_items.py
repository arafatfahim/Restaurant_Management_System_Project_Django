# Generated by Django 3.2 on 2022-04-24 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0013_remove_order_food_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='food_items',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='hotel.food'),
            preserve_default=False,
        ),
    ]
