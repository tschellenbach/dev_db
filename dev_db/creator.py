from dev_db.decorators import cached
from dev_db.dependencies import get_dependencies
from dev_db.utils import get_max_id, model_name, model_has_id_primary_key, \
    hash_instance
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_models
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class DevDBCreator(object):
    '''
    The dev creator class handles all the logic for creating a dev db sample from your main database

    It starts by getting the models it needs to run on
    - get_models
    - get_model_settings (determines how large a sample set we need for the given tables)
    - collect_data (actually retrieves the data)
    - extend_data (looks up the dependencies for the data)
    The extended data is ready for serialization
    '''
    exclude_content_type = False
    def get_models(self):
        '''
        Get models creates a list of models to create the dev db from
        - full required (a custom list of models which you want imported in full)
        - all valid_models (you can list excluded models in self.get_all_models())
        '''
        # these models go first
        full_required = self.get_full_required()
        excluded = self.get_excluded_models()
        all_models = self.get_all_models()
        valid_models = list(full_required)

        for m, n in all_models:
            # skip the ones already in full required
            if m in valid_models:
                continue
            table = m._meta.db_table
            # handle the excludes
            valid = True
            for e in excluded:
                if e in table:
                    valid = False
            if getattr(m._meta, 'proxy'):
                valid = False
            if valid:
                valid_models.append(m)
        return valid_models

    def get_model_settings(self):
        '''
        determines how large a sample set we need for the given tables
        '''
        models = self.get_models()
        model_settings = []
        full_required = self.get_full_required()

        for m in models:
            logger.info('getting settings for %s', m)
            max_id = get_max_id(m)
            if max_id > 50:
                limit = 10
            else:
                limit = 30
            if m in full_required:
                limit = 2000
            setting = (m, limit)
            model_settings.append(setting)
        return model_settings

    def collect_data(self, model_settings, limit=None, select_related=False):
        '''
        You can easily add more data by implementing get_custom_data
        '''
        # first add the data we are manually specifying
        logger.info('loading the custom data first')
        objects = self.get_custom_data()

        for (m, limit) in model_settings[:limit]:
            logger.info('getting %s items for model %s', limit, m)
            id_primary_key = model_has_id_primary_key(m)
            if id_primary_key:
                queryset = m._default_manager.all().order_by('-id')
            else:
                queryset = m._default_manager.all()
            if select_related:
                queryset = queryset.select_related()
            queryset = queryset[:limit]
            objects.extend(queryset)

        # filter out duplicates
        logger.info('removing duplicates from collect data step')
        objects = self.filter_data(objects)
        return objects

    def extend_data(self, data):
        '''
        Lookup the dependencies for our data
        '''
        logger.info('extending the data for %s instances', len(data))
        extended_data = []
        for instance in data:
            deps = self.get_dependencies(instance)
            extended_data += deps

        logger.info('extend completed, now %s instances', len(extended_data))
        return extended_data

    def get_dependencies(self, instance):
        '''
        Filter the dependencies because contenttype and permission are automagically created by django
        '''
        deps = get_dependencies(instance)
        if self.exclude_content_type:
            deps = [d for d in deps if not isinstance(
                d, (ContentType, Permission))]
        return deps

    @cached(key='cached_model_settings', timeout=60 * 10)
    def get_cached_model_settings(self):
        return self.get_model_settings()

    def get_full_required(self):
        return set()

    def get_excluded_models(self):
        excluded = [
            'celery',
            'djcelery',
            'djkombu',
            'sentry',
            'south',
            # skip user profile as it gets loaded when users are loaded
            'user_profile',
            # log entries arent very interesting either
            'log',
        ]
        if self.exclude_content_type:
            # special cases in django which get generated automatically
            excluded += ['content_type', 'permission']
        return excluded

    def get_all_models(self):
        return [(m, model_name(m)) for m in get_models()]

    def get_custom_data(self):
        logger.info('loading staff users')
        user_model = get_user_model()
        data = list(user_model.objects.filter(is_staff=True))

        return data

    def filter_data(self, data):
        logger.info('filtering data to unique instances')
        unique_set = set()
        filtered_data = []
        for instance in data:
            h = hash_instance(instance)
            if h not in unique_set:
                unique_set.add(h)
                filtered_data.append(instance)
        return filtered_data
