# Generated by Django 2.2.4 on 2019-08-22 06:03

from django.db import migrations, models
import django.db.models.deletion
import logs.models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0012_manualdataupload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesslog',
            name='target',
            field=models.ForeignKey(help_text='Title for which this log was created', null=True, on_delete=django.db.models.deletion.CASCADE, to='publications.Title'),
        ),
        migrations.AlterField(
            model_name='manualdataupload',
            name='data_file',
            field=models.FileField(upload_to=logs.models.where_to_store, validators=[logs.models.validate_mime_type, logs.models.check_can_parse]),
        ),
    ]
