import os
import time
from fabric.api import env, require, run, sudo, cd, local, get

# sync and migrate local db and start server
def restart(reboot=False):
    local('python manage.py makemigrations')
    local('python manage.py migrate')
    if reboot:
        fixtures = ['devgroups', 'devusers', 'devcursos', 'devalumnos', 'devprofesores', 
        'devcolegio', 'devtareas']
        for f in fixtures:
            local('python manage.py loaddata ' + f)
    local('python manage.py runserver 0.0.0.0:8000')

# reset local db and start server
def reboot():
    try:
        local('rm db.sqlite3')
    except:
        pass
    restart(True)