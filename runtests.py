import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
example_dir = os.path.join(current_dir, 'dev_db_example')

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    SETTINGS_LOCATION = 'dev_db_example.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = SETTINGS_LOCATION
    DJANGO_SETTINGS_MODULE = SETTINGS_LOCATION


def runtests(args=None):
    import pytest
    sys.path.append(example_dir)

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('tests')

    result = pytest.main(['dev_db'])
    sys.exit(result)


if __name__ == '__main__':
    runtests(sys.argv)
