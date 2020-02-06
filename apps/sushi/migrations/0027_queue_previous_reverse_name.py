# Generated by Django 2.2.9 on 2020-02-06 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sushi', '0026_customer_id_requestor_id_blank_fix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sushifetchattempt',
            name='queue_previous',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queue_following', related_query_name='queue_following', to='sushi.SushiFetchAttempt'),
        ),
    ]
