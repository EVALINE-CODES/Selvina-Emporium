# Generated by Django 5.0.4 on 2024-04-30 11:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("selvina_app", "0002_alter_product_image"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={"ordering": ["id"]},
        ),
    ]
