from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.management.base import BaseCommand
import os

fixtures = {}


def register(fixture_generator):
    fixtures[fixture_generator.name] = fixture_generator


class FixtureGenerator(object):
    '''
    Usually you'll want to replace
    
    - name
    - fixture_path (a list of, passed to os.path.join)
    - get_objects (returning the objects)
    
    Subsequently you should register your fixture generator
    
    
    **Examples**::
    
        class CommentFixture(FixtureGenerator):
            name = 'comment'
            fixture_path = ['py', 'user', 'fixtures', 'comments.json']
            
            def get_objects(self):
                content_types = []
                content_types.append(ContentType.objects.get(app_label="lists", model="userlist"))
                content_types.append(ContentType.objects.get(app_label="user", model="profile"))
                content_types.append(ContentType.objects.get(app_label="entity", model="entity"))
                
                comments = []
                for c in content_types:
                    from tcc.models import Comment
                    new_comments = list(Comment.objects.filter(content_type=c, object_pk__isnull=False)[:10])
                    new_comments = [c for c in new_comments if c.content_object][:1]
                    comments += new_comments
                    
                return comments
            
        register(CommentFixture)
        
        
        class CommunicationFixture(FixtureGenerator):
            name = 'communication'
            fixture_path = ['py', 'user', 'fixtures', 'communication.json']
            
            def get_objects(self):
                from user.models import Communication
                objects = list(Communication.objects.all()[:100])
                return objects
            
        register(CommunicationFixture)
    
    '''
    name = None
    fixture_path = None
    
    def get_objects(self):
        pass
    
    def regenerate(self):
        path = self.get_path()
        objects = self.get_objects_with_deps()
        data = serializers.serialize("json", objects, indent=4)
        out = open(path, "w")
        out.write(data)
        out.close()
    
    def get_path(self):
        path = os.path.join(settings.BASE_ROOT, *self.fixture_path)
        return path
    
    def cleanup(self, objects):
        # these are models we never want in a fixture
        to_remove = (ContentType, Permission, Group)
        cleaned_objects = []
        for object_ in objects:
            if not isinstance(object_, to_remove):
                cleaned_objects.append(object_)
        return cleaned_objects
    
    def get_objects_with_deps(self):
        from dev_db.dependencies import get_dependencies
        objects = self.get_objects()
        deps = []
        for object_ in objects:
            deps += get_dependencies(object_)
        objects += deps
        objects = self.cleanup(objects)
        return objects
            

class Command(BaseCommand):
    help = 'Get a list of the current settings'
    can_import_settings = True
    requires_model_validation = False

    def handle(self, *args, **options):
        for name, generator in fixtures.items():
            print name, generator
            instance = generator()
            instance.regenerate()
            print 'replaced fixture %s' % instance.get_path()

