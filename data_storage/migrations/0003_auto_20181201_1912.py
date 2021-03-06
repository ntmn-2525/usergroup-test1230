# Generated by Django 2.1.3 on 2018-12-01 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_storage', '0002_auto_20181201_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='category_code',
            field=models.ForeignKey(db_column='category_code', on_delete=django.db.models.deletion.CASCADE, to='data_storage.Category', to_field='code'),
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together={('category_code', 'code')},
        ),
    ]
