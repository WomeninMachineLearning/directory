import random
from django.core import management
from django.core.management.base import BaseCommand, CommandError

import main_app.settings as settings
from profiles.models import Country, User, Profile
from profiles.models import (
    METHODS_CHOICES,
    APPLICATIONS_CHOICES,
    MONTHS_CHOICES,
    POSITION_CHOICES,
    PRONOUN_CHOICES
)

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


        # Accounts

        n_profiles = kwargs['profiles']
        profiles = []
        for _ in range(n_profiles):

            methods = random.choice(METHODS_CHOICES)[0]
            applications = random.choice(APPLICATIONS_CHOICES)[0]

            grad_month = random.choice(MONTHS_CHOICES)[0]
            grad_year = str(random.randint(1950, 2020))

            name = random.choice(names)
            surname = random.choice(surnames)
            fullname = name + ' ' + surname
            institution = random.choice(institutions)
            slug = fullname.lower().replace(' ', '-')
            email = slug + '@' + institution.lower().replace(' ', '-') + '.edu'

            position = random.choice(POSITION_CHOICES)[0]
            preferred_pronoun = random.choice(PRONOUN_CHOICES)[0]
            other_pronoun = ''
            if preferred_pronoun == 'OTHER':
                other_pronoun = 'xey/xem/xyr'


            user = User.objects.create_user(
                username=name+surname+str(random.randint(1,100)),
                name=fullname,
                email=email,
                password='user'
            )
            user.save()     

            profile = Profile(
                user=user,
                first_name=name,
                last_name=surname,
                preferred_pronoun = preferred_pronoun,
                other_pronoun = other_pronoun,
                contact_email=email,
                webpage='http://'+slug+'.me',
                institution=institution,
                country=random.choice(countries),
                position=position,
                grad_month=grad_month,
                grad_year=grad_year,
                methods=methods,
                applications=applications,
                keywords='My long keyword that I want to see if it gets cut correctly for small screen sizes, Another long annoying keyword',
                is_public=random.random() > 0.2,
            )
            profiles += [profile]
            profile.save()


        management.call_command(
            'dumpdata',
            'profiles',
            'auth',
            natural_primary=True,
            natural_foreign=True,
            output='profiles/fixtures/database.json'
        )