import datetime
from django.db import models
from django.utils import timezone


# Create your models here.
class Article(models.Model):
    article_id = models.CharField(max_length=200, unique=True)
    title = models.TextField()
    subject = models.CharField(max_length=30)
    summary = models.TextField()
    published = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

    def __str__(self):
        return self.title[0:30]


class Author(models.Model):
    name = models.CharField(max_length=300, unique=True)
    articles = models.ManyToManyField(Article)

    def __str__(self):
        return self.name
