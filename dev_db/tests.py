from dev_db.creator import DevDBCreator
from dev_db.dependencies import get_dependencies, get_first_dependencies
from dev_db.utils import *
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase


class CreatorTestCase(TestCase):
    def setUp(self):
        self.creator = DevDBCreator()

    def test_model_listing(self):
        return
        self.creator.get_models()

    def test_model_settings(self):
        return
        self.creator.get_model_settings()

    def test_collect(self):
        return
        model_settings = self.creator.get_model_settings()
        data = self.creator.collect_data(model_settings)

    def test_dependency_lookup_user(self):
        '''
        Expected output is a sorted list like

        Site Category, Site, User, Entity, Love

        '''
        return
        from django.contrib.auth.models import User
        from user.models import Profile
        instance = User.objects.all()[:1][0]

        # check the one level deep case
        dependencies = get_first_dependencies(instance)
        if not isinstance(dependencies[1], Profile) or len(dependencies) != 2:
            raise ValueError
        # check the recursive approach
        dependencies = get_dependencies(instance)
        if not isinstance(dependencies[1], Profile) or len(dependencies) != 2:
            raise ValueError

    def test_dependency_lookup_love(self):
        '''
        Expected output is a sorted list like

        Site Category, Site, User, Entity, Love
        '''
        return
        from entity.models import Love
        from user.models import Profile
        from django.contrib.auth.models import User
        from entity.models import Entity, Site, SiteCategory
        instance = Love.objects.all()[:1][0]
        first_dependencies = get_first_dependencies(instance)
        first_models = [d.__class__ for d in first_dependencies]
        required_models = [User, User, Entity, Love]
        self.assertEqual(first_models, required_models)
        dependencies = get_dependencies(instance)
        models = [d.__class__ for d in dependencies]
        required_models = [User, Profile] * 3 + [SiteCategory,
                                                 Site, Entity, Love]
        self.assertEqual(models, required_models)

    def test_dependency_lookup_comment(self):
        return
        from entity.models import Love
        from user.models import Profile
        from django.contrib.auth.models import User
        from entity.models import Entity, Site, SiteCategory
        from tcc.models import Comment
        instance = Comment.objects.all()[:1][0]
        dependencies = get_dependencies(instance)
        models = [d.__class__ for d in dependencies]
        required_models = [User, Profile, SiteCategory, Site,
                           Entity, User, Profile, ContentType, Comment]
        self.assertEqual(models, required_models)

    def test_filter_step(self):
        '''
        takes a list like
        Site Category, Site, User, Entity, Love Site Category, Site, User, Entity, Love

        and removes duplicates (keeping only the first occurrence)
        '''
        return
