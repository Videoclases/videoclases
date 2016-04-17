import json

import datetime
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        name_files = ['fixtures/devcourses.json']
        for filename in name_files:
            file = None
            with open(filename, 'r') as file_to_update:
                file = file_to_update.read()
            with open(filename, 'w') as file_to_update:
                new_data = []
                for item in json.loads(file):
                    new_dict = item
                    if 'fields' in item:
                        if 'year' in item['fields']:
                            new_dict['fields']['year'] = datetime.datetime.now().year
                    new_data.append(new_dict)
                file_to_update.write(json.dumps(new_data, indent=4))
