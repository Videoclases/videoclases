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

from videoclases.models import *

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
    username = raw_input('Insert username: ')
    password = getpass.getpass('Insert password: ')
    password2 = getpass.getpass('Confirm password: ')
    while password != password2:
        print 'Passwords were not equal.'
        password = getpass.getpass('Insert password again: ')
        password2 = getpass.getpass('Confirm password: ')
    first_name = raw_input('Insert first name: ')
    last_name = raw_input('Insert last name: ')
    colegio = raw_input('Insert school name: ')
    curso = raw_input('Insert course name: ')
    user = User.objects.create_user(username=username, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    Colegio.objects.create(nombre=colegio).save()
    co = Colegio.objects.get(nombre=colegio)
    Curso.objects.create(nombre=curso, colegio=co, anho=timezone.now().year).save()
    cu = Curso.objects.get(nombre=curso, colegio=co, anho=timezone.now().year)
    Profesor.objects.create(usuario=user, colegio=co)
    p = Profesor.objects.get(usuario=user, colegio=co)
    p.cursos.add(cu)
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