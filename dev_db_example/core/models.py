from django.db import models
from django.contrib.auth.models import User
# Create your models here.



'''
Some example models to demo the dev_db script
'''


class SiteCategory(models.Model):
    name = models.CharField(max_length=255)

    
class Site(models.Model):
    category = models.ForeignKey(SiteCategory)
    #url = models.TextField()

    
class Tag(models.Model):
    name = models.CharField(max_length=25)

    
class Item(models.Model):
    site = models.ForeignKey(Site)
    url = models.TextField()
    user = models.ForeignKey(User)
    
    tags = models.ManyToManyField(Tag)
    

    

