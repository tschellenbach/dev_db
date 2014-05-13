
from functools import wraps
from django.utils.decorators import available_attrs


def simplify_class_decorator(class_decorator):
    '''
    Makes the decorator syntax uniform
    Regardless if you call the decorator like
        @decorator
        or
        @decorator()
        or
        @decorator(staff=True)

    Complexity, Python's class based decorators are weird to say the least:
    http://www.artima.com/weblogs/viewpost.jsp?thread=240845

    This function makes sure that your decorator class always gets called with
    __init__(fn, *option_args, *option_kwargs)
    __call__()
        return a function which accepts the *args and *kwargs intended
        for fn
    '''
    # this makes sure the resulting decorator shows up as
    # function FacebookRequired instead of outer
    @wraps(class_decorator)
    def outer(fn=None, *decorator_args, **decorator_kwargs):
        # wraps isn't needed, the decorator should do the wrapping :)
        # @wraps(fn, assigned=available_attrs(fn))
        def actual_decorator(fn):
            instance = class_decorator(fn, *decorator_args, **decorator_kwargs)
            _wrapped_view = instance.__call__()
            return _wrapped_view

        if fn is not None:
            wrapped_view = actual_decorator(fn)
        else:
            wrapped_view = actual_decorator

        return wrapped_view
    return outer


class CachedDecorator(object):

    """
    Decorator which cached the call to the give function. Usage example ::

    @cached(key='notification_settings_%(user_id)s', timeout=60 * 10)

    For people which got tired of typing ::

    key_format = 'my_format_%(user_id)s'
    key = key_format % dict(user_id=user_id)
    data = cache.get(key)

    if data is None:
        data = range(10, 20)
        #or any other stuff here
        cache.set(key, data, timeout=50)

    return data
    """

    def __init__(self, fn, key, timeout):
        '''
        :param fn: the function passed to the decorator
        :param key: a python format string used for determining the key, ie 'key_%(user_id)s'
        :param timeout: timeout in seconds
        '''
        self.fn = fn
        self.key = key
        self.timeout = timeout

    def __call__(self):
        '''
        When the decorator is called like this
            @cached
            The call will receive

        Otherwise it will be like
            @cached()
            The init will receive the parameters
        '''
        @wraps(self.fn, assigned=available_attrs(self.fn))
        def wrapped_view(*args, **kwargs):
            response = self.cached(self.fn, *args, **kwargs)
            return response

        return wrapped_view

    def cached(self, fn, *args, **kwargs):
        '''
        try the cache and fallback to the function
        '''
        from django.core.cache import cache
        # simplify to only using kwargs for easy key string formatting
        args, kwargs = self.args_to_kwargs(fn, args, kwargs)

        key = self.key % kwargs
        timeout = self.timeout

        data = cache.get(key)

        if data is None:
            data = fn(**kwargs)
            cache.set(key, data, timeout)

        return data

    def args_to_kwargs(self, fn, args, kwargs):
        '''
        Turn arg bassed calls to kwargs
        '''
        import inspect
        argnames, varargs, keywords, defaults = inspect.getargspec(fn)
        arg_kwargs = dict(zip(argnames, args))
        kwargs.update(arg_kwargs)
        args = []
        return args, kwargs

cached = simplify_class_decorator(CachedDecorator)
