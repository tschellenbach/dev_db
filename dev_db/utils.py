
'''
Model level functions
'''
import time


def get_max_id(m):
    max_id = 0
    id_primary_key = model_has_id_primary_key(m)
    if id_primary_key:
        instances = list(m._default_manager.all().order_by('-id')[:1])
        if instances:
            max_id = getattr(instances[0], 'id', 0)
    return max_id


def get_field_names(m):
    field_names = [f.name for f in m._meta.fields]
    return field_names


def model_has_id_primary_key(m):
    field_names = get_field_names(m)
    id_primary_key = 'id' in field_names
    return id_primary_key


def model_name(m):
    module = m.__module__.split('.')[:-1]  # remove .models
    return ".".join(module + [m._meta.object_name])


'''
Instance level functions
'''


def get_all_fields(instance):
    # follow forward relation fields
    normal_fields = instance.__class__._meta.fields
    many_to_many_fields = instance.__class__._meta.many_to_many
    virtual_fields = instance.__class__._meta.virtual_fields
    all_fields = normal_fields + many_to_many_fields + virtual_fields
    return all_fields


def hash_instance(instance):
    return hash((instance.__class__, instance.pk))


'''
General utilities
'''


def get_creator_instance():
    creator_class = get_creator_class()
    return creator_class()


def get_creator_class():
    from django.conf import settings
    default = 'dev_db.creator.DevDBCreator'
    creator_class_string = getattr(settings, 'DEV_DB_CREATOR', default)
    creator_class = get_class_from_string(creator_class_string)
    return creator_class


def get_class_from_string(path, default='raise'):
    """
    Return the class specified by the string.

    IE: django.contrib.auth.models.User
    Will return the user class

    If no default is provided and the class cannot be located
    (e.g., because no such module exists, or because the module does
    not contain a class of the appropriate name),
    ``django.core.exceptions.ImproperlyConfigured`` is raised.
    """
    from django.core.exceptions import ImproperlyConfigured
    backend_class = None
    try:
        from importlib import import_module
    except ImportError:
        from django.utils.importlib import import_module
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error loading registration backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        if default == 'raise':
            raise ImproperlyConfigured(
                'Module "%s" does not define a registration '
                'backend named "%s"' % (module, attr))
        else:
            backend_class = default
    return backend_class


class timer(object):
    def __init__(self):
        self.times = [time.time()]
        self.total = 0.
        self.next()

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        times = self.times
        times.append(time.time())
        delta = times[-1] - times[-2]
        self.total += delta
        return delta

    def get_avg(self, default=None):
        if self.times:
            return self.total / len(self.times)
        else:
            return default

    avg = property(get_avg)
