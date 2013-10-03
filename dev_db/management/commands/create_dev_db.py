"""
Dumps data from the main database, but only dumps a subset of the items
To ensure we can load them on the development server

We use this because the production database became too heavy to load even with
optimized tools like pg_dump

This script follows relations to ensure referential integrity so if you load
blog_post, it will ensure the author is also serialized
"""
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from dev_db.utils import timer
import logging
from dev_db.utils import get_creator_instance
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
        make_option('-o', '--output', default=None, dest='output', type='string',
                    help='Path of the output file'),
        make_option(
            '--skipcache', default=False, dest='skipcache', action='store_true',
            help='Skips the settings cache'),
    )

    def handle(self, **options):
        # setup the options
        self.format = options.get('format', 'json')
        self._validate_serializer(self.format)
        self.indent = options.get('indent', 4)
        self.limit = options.get('limit')
        output = options.get('output')
        self.output = None
        if output:
            self.output_path = os.path.abspath(output)
            self.output = open(self.output_path, 'w')
        self.skipcache = options.get('skipcache')
        logger.info(
            'serializing using %s and indent %s', self.format, self.indent)

        t = timer()
        creator = get_creator_instance()
        logger.info('using creator instance %s', creator)
        if self.skipcache:
            logger.info('skipping the cache')
            model_settings = creator.get_model_settings()
        else:
            model_settings = creator.get_cached_model_settings()

        logger.info('model_settings lookup took %s', t.next())
        data = creator.collect_data(
            model_settings, limit=self.limit, select_related=False)
        logger.info('data collection took %s', t.next())
        extended_data = creator.extend_data(data)
        logger.info('extending data took %s', t.next())
        filtered_data = creator.filter_data(extended_data)
        logger.info('filtering data took %s', t.next())
        logger.info('serializing data with format %s', self.format)
        serialized = serializers.serialize(self.format, filtered_data, indent=self.indent, use_natural_keys=False)
        # write the output
        if self.output:
            self.output.write(serialized)
        logger.info('serializing data took %s', t.next())
        logger.info('total duration %s', t.total)
        return serialized

    def _validate_serializer(self, format):
        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)
