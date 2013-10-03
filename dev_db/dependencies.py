from dev_db.utils import get_all_fields
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.auth.models import SiteProfileNotAvailable


def get_dependencies(instance, dependencies=None):
    '''
    Recurses through the results and finds the dependencies

    Example:
    Love -> deps == (User, User, Entity, Love)

    Recurse
    (User, Profile, User, Profile, Site, Entity, Love)

    Recurse
    (User, Profile, User, Profile, Site Category, Site, Entity, Love)
    '''
    # set the defaults
    if dependencies is None:
        dependencies = []

    # see the dependencies for this instance
    deps = get_first_dependencies(instance)
    # prevent infinite loops, usually between profile and user
    deps = [d for d in deps if d not in dependencies]
    # for the first iteration (User, User, Entity, Love)
    for d in deps:
        # this is the case when its Love
        if d == instance:
            dependencies.append(d)
        # this happens for (Entity, User
        else:
            get_dependencies(d, dependencies)

    return dependencies


def get_first_dependencies(instance):
    '''
    Returns all dependencies for this instance and the instance itself
    in the right order

    Note: Only goes one level deep
    '''
    # exception for profiles
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()

    # get all fields for this instance
    all_fields = get_all_fields(instance)

    dependencies = [instance]
    # iterate over all fields
    for f in all_fields:
        # handle the base case with foreign keys
        # handle the more complicated generic foreign keys
        if isinstance(f, (ForeignKey, GenericForeignKey)):
            new = getattr(instance, f.name)
            if new:
                dependencies.insert(0, new)

        # handle many to many fields, we need to support this as django will attempt
        # to serialize them when serializing related items
        if isinstance(f, ManyToManyField):
            for new in getattr(instance, f.name).all():
                if new:
                    dependencies.insert(0, new)

    #hack for profile models
    if isinstance(instance, UserModel):
        try:
            profile = instance.get_profile()
        except SiteProfileNotAvailable, e:
            profile = None
        if profile:
            dependencies.append(profile)

    return dependencies
