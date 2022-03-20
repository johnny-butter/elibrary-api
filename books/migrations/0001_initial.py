# Generated by Django 3.2.11 on 2022-01-19 03:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(blank=True, max_length=128, null=True)),
                ('author', models.CharField(blank=True, max_length=128, null=True)),
                ('publisher', models.CharField(blank=True, max_length=128, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('stock', models.IntegerField(default=0)),
                ('is_vip_only', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(null=True)),
            ],
        ),
    ]