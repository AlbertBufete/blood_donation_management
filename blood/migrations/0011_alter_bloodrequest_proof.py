# Generated by Django 4.1.5 on 2023-01-20 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0010_bloodrequest_proof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodrequest',
            name='proof',
            field=models.ImageField(blank=True, null=True, upload_to='proof/'),
        ),
    ]
