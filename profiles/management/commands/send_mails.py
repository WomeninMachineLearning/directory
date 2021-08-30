from django.core import management
from django.core.management.base import BaseCommand, CommandError
import main_app.settings as settings

from profiles.emails import user_create_confirm_email
from profiles.models import User

class Command(BaseCommand):
    help = 'Send available e-mails for testing purpose.'

    def add_arguments(self, parser):
        parser.add_argument('email', help='E-mail to send to')

    def handle(self, *args, **kwargs):
        u = User(email=kwargs['email'])
        user_create_confirm_email(u).send()