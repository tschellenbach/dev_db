from dev_db.creator import DevDBCreator
from dev_db.dependencies import get_dependencies, get_first_dependencies
from dev_db.utils import *
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase


class CreatorTestCase(TestCase):
    fixtures = ['example.json']

    def setUp(self):
        from core.dev_db_creator import ExampleDevDBCreator
        self.creator = ExampleDevDBCreator()

    def test_model_listing(self):
        listed_models = self.creator.get_models()
        
    def test_recursion(self):
        from core.models import Post
        post = Post.objects.get(pk=1)
        deps = get_dependencies(post)
        correct_deps = [post, post.blogger, post]
        self.assertEqual(correct_deps, deps)

    def test_model_settings(self):
        model_settings = self.creator.get_model_settings()
        from django.contrib.sessions.models import Session
        from django.contrib.auth.models import User, Permission, Group
        from django.contrib.sites.models import Site as DjangoSite
        from django.contrib.contenttypes.models import ContentType
        from core.models import SiteCategory, Site, Tag, Item, Post
        expected_result = [
            (SiteCategory, 30),
            (Site, 30),
            (Tag, 30),
            (Item, 30),
            (Post, 30),
            (Session, 30),
            (DjangoSite, 30),
            (Permission, 30),
            (Group, 30),
            (User, 30),
            (ContentType, 30),
        ]
        self.assertEqual(model_settings, expected_result)

    def test_collect(self):
        model_settings = self.creator.get_model_settings()
        data = self.creator.collect_data(model_settings)

    def test_dependency_lookup_site(self):
        '''
        Expected output is a sorted list like

        Site Category, Site, User, Entity, Love

        '''
        from core.models import Site, SiteCategory
        site = Site.objects.all()[:1][0]
        # check the recursive approach
        dependencies = get_dependencies(site)
        correct_deps = [site.category, site]
        self.assertEqual(correct_deps, dependencies)

    def test_dependency_lookup_item(self):
        '''
        Expected output is a sorted list like

        Site Category, Site, User, Entity, Love

        '''
        from core.models import Item
        instance = Item.objects.all()[:1][0]
        # check the recursive approach
        dependencies = get_dependencies(instance)
        correct_deps = list(instance.tags.all())[::-1] + [instance.user,
                                                          instance.site.category, instance.site, instance]
        self.assertEqual(dependencies, correct_deps)

    def test_filter_step(self):
        '''
        takes a list like
        Site Category, Site, User, Entity, Love Site Category, Site, User, Entity, Love

        and removes duplicates (keeping only the first occurrence)
        '''
        from core.models import Item
        instance = Item.objects.all()[:1][0]
        list_with_duplicates = [instance.user, instance, instance.user]
        correct_result = [instance.user, instance]
        result = self.creator.filter_data(list_with_duplicates)
        self.assertEqual(result, correct_result)

    def test_full_create(self):
        '''
        For now just make sure it doesnt produce errors
        '''
        from django.core import serializers
        model_settings = self.creator.get_model_settings()
        data = self.creator.collect_data(model_settings)
        extended_data = self.creator.extend_data(data)
        filtered_data = self.creator.filter_data(extended_data)
        serialized = serializers.serialize(
            'json', filtered_data, indent=4, use_natural_keys=True)
