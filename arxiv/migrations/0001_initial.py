# Generated by Django 2.2.5 on 2020-02-17 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_id', models.CharField(max_length=200, unique=True)),
                ('title', models.TextField()),
                ('subject', models.CharField(max_length=30)),
                ('summary', models.TextField()),
                ('published', models.DateTimeField(verbose_name='date published')),
                ('updated', models.DateTimeField(verbose_name='date updated')),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, unique=True)),
                ('articles', models.ManyToManyField(to='arxiv.Article')),
            ],
        ),
    ]