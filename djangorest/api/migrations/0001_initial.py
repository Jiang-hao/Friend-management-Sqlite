# Generated by Django 2.0.2 on 2018-03-10 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friends', models.CharField(max_length=200, null=True)),
                ('blocked_friends', models.CharField(max_length=200, null=True)),
                ('follower', models.CharField(max_length=200, null=True)),
                ('follow', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('name', models.CharField(max_length=200, primary_key=True, serialize=False, unique=True)),
                ('post_message', models.CharField(default='', max_length=200)),
                ('received_message', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='friends',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Person'),
        ),
    ]
