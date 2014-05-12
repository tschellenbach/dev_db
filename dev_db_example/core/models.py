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
    
# these two models are here to test if things break
# when relations go two ways (infinite loops etcs)
    
class Blogger(models.Model):
    name = models.CharField(max_length=255)
    favourite_post = models.ForeignKey('Post', related_name='favourites')
    
class Post(models.Model):
    blogger = models.ForeignKey(Blogger)
    
    

    

