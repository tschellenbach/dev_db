from django.contrib import admin
from core import models as core_models
from django.db.models.base import ModelBase
import inspect

for k, m in inspect.getmembers(core_models, lambda x: isinstance(x, ModelBase)):
    if m.__module__ == core_models.__name__:
        admin.site.register(m)
