import os
import time
from fabric.api import env, require, run, sudo, cd, local, get

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

def install():
    local('cp videoclases/project/settings_secret.py.template videoclases/project/settings_secret.py')
    _load_data()
    local('python manage test')
    local('python manage.py runserver 0.0.0.0:8000')

def install_with_data():
    local('cp videoclases/project/settings_secret.py.template videoclases/project/settings_secret.py')
    _load_data(True)
    local('python manage test')
    local('python manage.py runserver 0.0.0.0:8000')