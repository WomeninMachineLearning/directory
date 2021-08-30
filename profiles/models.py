from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from multiselectfield import MultiSelectField

US = 'Undergraduate student'
MS = 'Masters student'
PD = 'Predoc/postbac fellow/resident'
PHD = 'PhD student'
PDR = 'Post-doctoral researcher'
JRE = 'Research scientist/engineer'
SRE = 'Senior research scientist/engineer'
JDS = 'Data scientist/engineer'
RDS = 'Senior data scientist/engineer'
SWE = 'Software engineer'
LEC = 'Lecturer'
ATP = 'Assistant Professor'
ACP = 'Associate Professor'
PRF = 'Professor'
PM = 'Program/product manager'
DIR = 'Director/founder/advisor'

POSITION_CHOICES = (
    (US,'Undergraduate student'),
    (MS, 'Masters student'),
    (PD, 'Predoc/postbac fellow/resident'),
    (PHD, 'PhD student'),
    (PDR, 'Post-doctoral researcher'),
    (JRE, 'Research scientist/engineer'),
    (SRE, 'Senior research scientist/engineer'),
    (JDS, 'Data scientist/engineer'),
    (RDS, 'Senior data scientist/engineer'),
    (SWE, 'Software engineer'),
    (LEC, 'Lecturer'),
    (ATP, 'Assistant Professor'),
    (ACP, 'Associate Professor'),
    (PRF, 'Professor'),
    (PM, 'Program/product manager'),
    (DIR, 'Director/founder/advisor'),
)

MONTHS_CHOICES = (
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December')
)

METHODS_CHOICES = (
    ('SL', 'Supervised learning'),
    ('UL', 'Unsupervised learning'),
    ('ALG', 'Algorithms: active, online, multi-task learning, etc.'),
    ('DL', 'Deep learning'),
    ('RL', 'Reinforcement learning and planning'),
    ('REL', 'Representation learning'),
    ('PR', 'Probabilistic methods'),
    ('OPT','Optimization methods'),
    ('LT', 'Learning theory'),
    ('TR', 'Trustworthy ML'),
    ('HAI', 'Humans and AI'),
)

APPLICATIONS_CHOICES = (
    ('AUD', 'Audio and Speech Processing'),
    ('CV', 'Computer Vision'),
    ('NLP', 'Natural Language Processing (NLP)'),
    ('TS', 'Time Series Analysis'),
    ('ROB', 'Robotics'),
    ('CB', 'Computational biology'),
    ('NS', 'Neuroscience'),
    ('PS', 'Physical sciences'),
    ('HC', 'Healthcare'),
    ('SG', 'Social good'),
    ('CS', 'Climate science'),
    ('DEP', 'Deployment of AI/ML systems')
)


class Country(models.Model):
    code = models.CharField(max_length=3, blank=False, unique=True)
    name = models.CharField(max_length=60, blank=False)
    is_under_represented = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'countries'
        ordering = ['name']

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The email must be set'))

        extra_fields.setdefault('is_active', True)
        
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        super_user = self.create_user(email, password, **extra_fields)
        super_user.is_superuser = True
        super_user.is_staff = True
        super_user.save(using=self._db)
        return super_user


class User(AbstractBaseUser, PermissionsMixin):

    username = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def first_name(self):
        return self.name.split(' ', 1)[0]


class Profile(models.Model):

    @classmethod
    def get_position_choices(cls):
        return POSITION_CHOICES

    @classmethod
    def get_methods_choices(cls):
        return METHODS_CHOICES

    @classmethod
    def get_applications_choices(cls):
        return APPLICATIONS_CHOICES

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)

    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    contact_email = models.EmailField(blank=True)
    webpage = models.URLField(blank=True)
    institution = models.CharField(max_length=100, blank=False)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='profiles',
                                null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES,
                                blank=True)
    grad_month = models.CharField(max_length=2, choices=MONTHS_CHOICES,
                                  blank=True)
    grad_year = models.CharField(max_length=4, blank=True)
    methods = MultiSelectField(choices=METHODS_CHOICES, blank=True)
    applications = MultiSelectField(choices=APPLICATIONS_CHOICES, blank=True)
    keywords = models.CharField(max_length=250, blank=True)
    publish_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'institution', 'last_updated']

    def __str__(self):
        return f'{self.name}, {self.institution}'

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.id})

    def methods_labels(self):
        return [dict(METHODS_CHOICES).get(item, item)
                for item in self.methods]

    def applications_labels(self):
        return [dict(APPLICATIONS_CHOICES).get(item, item)
                for item in self.applications]

    def grad_month_labels(self):
        return dict(MONTHS_CHOICES).get(self.grad_month)