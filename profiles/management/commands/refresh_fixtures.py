import random
from django.db import connection
from django.core import management
from django.core.management.color import no_style
from django.core.management.base import BaseCommand, CommandError

import winrepo.settings as settings
from profiles.models import Country, Profile

class Command(BaseCommand):
    help = 'Re-create fixtures based on models'

    def add_arguments(self, parser):
        parser.add_argument('--seed', default=1, type=int, help='Random Seed')
        parser.add_argument('--profiles', default=10, type=int, help='Number of profiles to be created')

    def handle(self, *args, **kwargs):

        if not settings.DEBUG:
            raise CommandError('Please, do not run this command on production mode. It will wipe the database.')

        random.seed(kwargs['seed'])

        management.call_command(
            'flush',
            no_input=True,
            interactive=False,
        )

        countries_data = []
        with open('profiles/fixtures/countries.txt') as f:
            countries_data = [c.split('\t') for c in f.read().splitlines()]

        Country.objects.all().delete()

        countries = []
        for name, code in countries_data:
            is_under_represented = random.random() > 0.5

            country =  Country(
                code=code,
                name=name,
                is_under_represented=is_under_represented,
            )
            country.save()
            countries += [country]


        institutions = []
        with open('profiles/fixtures/institutions.txt') as f:
            institutions = f.read().splitlines()


        names = []
        surnames = []
        with open('profiles/fixtures/names.txt') as f:
            fullnames = [n.split(' ') for n in f.read().splitlines()]
            names = [n[0] for n in fullnames]
            surnames = [n[1] for n in fullnames]


        Profile.objects.all().delete()

        n_profiles = kwargs['profiles']
        profiles = []
        for _ in range(n_profiles):

            brain_structure = random.choice(Profile.STRUCTURE_CHOICES)[0]
            modalities = random.choice(Profile.MODALITIES_CHOICES)[0]
            methods = random.choice(Profile.METHODS_CHOICES)[0]
            domains = random.choice(Profile.DOMAINS_CHOICES)[0]

            grad_month = random.choice(Profile.MONTHS_CHOICES)[0]
            grad_year = str(random.randint(1950, 2020))

            name = random.choice(names)
            surname = random.choice(surnames)
            fullname = name + ' ' + surname
            institution = random.choice(institutions)
            slug = fullname.lower().replace(' ', '-')
            email = slug + '@' + institution.lower().replace(' ', '-') + '.edu'

            position = random.choice(Profile.POSITION_CHOICES)[0]

            profile = Profile(
                name=fullname,
                email=email,
                webpage=slug + '.me',
                institution=institution,
                country=random.choice(countries),
                position=position,
                grad_month=grad_month,
                grad_year=grad_year,
                brain_structure=brain_structure,
                modalities=modalities,
                methods=methods,
                domains=domains,
                keywords='',
            )
            profiles += [profile]
            profile.save()

        management.call_command(
            'dumpdata',
            'profiles',
            natural_foreign=True,
            output='profiles/fixtures/winrepo.json'
        )