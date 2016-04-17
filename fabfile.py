from fabric.contrib import django as ddd
import django

ddd.project("project")
django.setup()

import getpass
import os
import time

from django.contrib.auth.models import User
from django.utils import timezone
from fabric.api import env, require, run, sudo, cd, local, get

from project.fabfile_secret import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_name = 'videoclases/project/settings_secret.py'
template_name = 'videoclases/project/settings_secret.py.template'

def _load_data(reboot=False):
    local('python manage.py makemigrations')
    local('python manage.py migrate')
    if reboot:
        fixtures = ['devgroups', 'devusers', 'devcolegio', 'devcursos', 'devalumnos', 'devprofesores', 
        'devtareas']
        for f in fixtures:
            local('python manage.py loaddata ' + f)

# fab devserver -> states that you will connect to devserver server
def devserver():
    env.hosts = [env.server_name]

# activates videoclases virtualenv in server
def virtualenv(command, use_sudo=False):
    if use_sudo:
        func = sudo
    else:
        func = run
    func('source %sbin/activate && %s' % (env.virtualenv_root, command))

# creates file in ~/
# usage: fab devserver test_connection
def test_connection():
    require('hosts', provided_by=[devserver])
    virtualenv('echo "It works!" > fabric_connection_works.txt')

# util for prompt confirmation
def _confirm():
    prompt = "Please confirm you want to sync the branch 'master' in the server 'buho'"
    prompt = '%s [%s/%s]: ' % (prompt, 'y', 'n')

    while True:
        ans = raw_input(prompt)
        if not ans:
            print 'Please answer Y or N.'
            continue
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'Please answer Y or N.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

# updates dev server project from git repository
def update():
    require('hosts', provided_by=[devserver])
    with cd(env.repo_root):
        run('git pull origin master')

# installs requirements in server
def install_requirements():
    require('hosts', provided_by=[devserver])
    virtualenv('pip install -q -r %(requirements_file)s' % env)

# aux function for calling manage.py functions
def manage_py(command, use_sudo=False):
    require('hosts', provided_by=[devserver])
    with cd(env.manage_dir):
        virtualenv('python manage.py %s' % command, use_sudo)

# syncs db in server
def makemigrations():
    require('hosts', provided_by=[devserver])
    manage_py('makemigrations')

# south migrate for db
def migrate():
    require('hosts', provided_by=[devserver])
    manage_py('migrate')

# collects static files
def collectstatic():
    require('hosts', provided_by=[devserver])
    manage_py('collectstatic --noinput')

# restarts apache in server
def reload():
    require('hosts', provided_by=[devserver])
    sudo('service apache2 restart')

# deploy on development server
def deploy():
    require('hosts', provided_by=[devserver])
    if _confirm():
        update()
        install_requirements()
        makemigrations()
        migrate()
        collectstatic()
        reload()
    else:
        print 'Deploy cancelado'

# sync and migrate local db and start server
def restart(reboot=False):
    _load_data(reboot)
    local('python manage.py runserver 0.0.0.0:8000')

# reset local db and start server
def reboot():
    try:
        local('rm db.sqlite3')
    except:
        pass
    restart(True)

def _create_teacher():
    print '---------------------------------------'
    print 'Now you will be asked for the necessary data to create a Professor.'

    from videoclases.models.course import Course
    from videoclases.models.teacher import Teacher
    from videoclases.models.school import School

    username = raw_input('Insert username: ')
    password = getpass.getpass('Insert password: ')
    password2 = getpass.getpass('Confirm password: ')
    while password != password2:
        print 'Passwords were not equal.'
        password = getpass.getpass('Insert password again: ')
        password2 = getpass.getpass('Confirm password: ')
    first_name = raw_input('Insert first name: ')
    last_name = raw_input('Insert last name: ')
    school = raw_input('Insert school name: ')
    course = raw_input('Insert course name: ')
    user = User.objects.create_user(username=username, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    School.objects.create(name=school).save()
    co = School.objects.get(name=school)
    Course.objects.create(name=course, school=co, year=timezone.now().year).save()
    cu = Course.objects.get(name=course, school=co, year=timezone.now().year)
    Teacher.objects.create(user=user, school=co)
    p = Teacher.objects.get(user=user, school=co)
    p.courses.add(cu)
    p.save()

def install():
    local('cp ' + os.path.join(BASE_DIR, template_name) + ' ' + os.path.join(BASE_DIR, file_name))
    _load_data()
    local('python manage.py collectstatic --noinput -l')
    local('python manage.py test')
    local('python manage.py loaddata devgroups')
    _create_teacher()
    local('python manage.py runserver 0.0.0.0:8000')

def install_with_data():
    local('cp ' + os.path.join(BASE_DIR, template_name) + ' ' + os.path.join(BASE_DIR, file_name))
    _load_data(True)
    local('python manage.py collectstatic --noinput -l')
    local('python manage.py test')
    local('python manage.py runserver 0.0.0.0:8000')