# Generated by Django 3.2 on 2022-04-24 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0007_userorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='price',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='FoodPrice', to='hotel.food'),
            preserve_default=False,
        ),
    ]