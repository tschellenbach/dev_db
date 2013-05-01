from fabric.api import local, cd
import os
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, '../'))


def publish(test='yes'):
    '''
    Easy publishing of my nice open source project
    '''
    if test == 'yes':
        validate()

    local('git push')

    from dev_db import __version__
    tag_name = 'v%s' % __version__
    local('python setup.py sdist upload')

    local('git tag %s' % tag_name)
    local('git push origin --tags')


def validate():
    with cd(PROJECT_ROOT):
        local('pep8 --exclude=migrations --ignore=E501,E225 dev_db')
        local('pyflakes.py -x W dev_db')
        local('python dev_db_example/manage.py test dev_db')


def clean():
    local('bash -c "autopep8 -i *.py"')
    local('bash -c "autopep8 -i dev_db/*.py"')
    local('bash -c "autopep8 -i dev_db/management/commands/*.py"')
