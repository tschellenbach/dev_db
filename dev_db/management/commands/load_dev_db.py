"""
Dumps data from the main database, but only dumps a subset of the items
To ensure we can load them on the development server

We use this because the production database became too heavy to load even with
optimized tools like pg_dump

This script follows relations to ensure referential integrity so if you load
blog_post, it will ensure the author is also serialized
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from optparse import make_option
import logging
import os

logger = logging.getLogger(__name__)
DEBUG = False


class Command(BaseCommand):
    help = 'Output a sample of the database as a fixture of the given format.'
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent', default=4, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('--limit', default=None, dest='limit', type='int',
            help='Allows you to limit the number of tables, used for testing purposes only'),
        make_option('--skipcache', default=False, dest='skipcache', action='store_true',
            help='Skips the settings cache'),
    )
    
    def handle(self, **options):
        # setup the options
        from django.db import connections
        db_host = connections['default'].settings_dict['HOST']
        if 'goteam' in db_host:
            raise ValueError('check your config %s looks like a production db' % db_host)
        logger.info('syncdb all')
        call_command('syncdb', migrate_all=True, interactive=False)
        logger.info('faking migrate')
        call_command('migrate', fake=True, interactive=False)
        cursor = connections['default'].cursor()
        self.truncate_permissions_etc(cursor)
        
        fixture_path = os.path.join(settings.BASE_ROOT, 'development_data.json.gz')
        logger.info('loading the fixture from %s', fixture_path)
        # clear the content type cache to prevent very interesting results
        ContentType.objects.clear_cache()
        call_command('loaddata', fixture_path, traceback=True, verbosity='2')
        
    def truncate_permissions_etc(self, cursor):
        logger.info('truncating content types')
        cursor.execute('TRUNCATE django_content_type CASCADE')
        logger.info('truncating auth_permissions')
        cursor.execute('TRUNCATE auth_permission CASCADE')
        
        