Django development database
===========================

Tool to automatically create a development database for local development by sampling your production database.
It maintains referential integrity by looking up the dependencies for the selected rows.


Creating the data
=================

```bash
  python manage.py create_dev_db > ../development_data.json
  gzip ../development_data.json
```

Creating the test fixture takes about 5-10 minutes

Loading the data
================

start with an empty db on local called 
test_fashiolista_local

1. python manage.py syncdb --all --noinput
2. python manage.py migrate --fake --noinput
3. Truncate contenttype and permission tables
4. python manage.py loaddata ../development_data.json.gz --traceback -v2

These four steps are also wrapped in the load_dev_db command. So simply run

```bash
  python manage.py load_dev_db
```

Loading the fixture takes about 2 minutes

(be sure to run pgtune on your local postgres, otherwise it might take longer)
