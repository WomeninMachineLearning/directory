from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from dal.autocomplete import ModelSelect2
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=False)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'name',
            'email',
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'institution',
            'country',
            'contact_email',
            'webpage',
            'position',
            'grad_month',
            'grad_year',
            'methods',
            'applications',
            'keywords',
        )
        labels = {
            'first_name': _('First name, as you would like it to appear publicly'),
            'last_name': _('Last name, as you would like it to appear publicly'),
            'institution': _('Institution/Company'),
            'contact_email': _('Contact email address'),
            'webpage': _('Linked In or web page'),
            'grad_month': _('Date PhD was obtained: Month'),
            'grad_year': _('Year'),
            'methods': _('Field of Research - Methods'),
            'applications': _('Field of Research - Applications'),
            'keywords': _('Field of Research - Keywords'),
        }
        help_texts = {
            'contact_email': _('A public email address for contact, typically '
                        'institutional (avoid using a personal address).'),
            'country': _('Country of the institution'),
            'webpage': _('Make sure people can look you up easily by '
                         'providing a link to a personal website, profile '
                         'or institution site.'),
            'position': _('Please choose your \'highest\' title from the '
                          'proposed options to ease future searches.'),
            'grad_month': _('Leave empty if no PhD (yet).'),
            'grad_year': _('Please enter the full year (4 digits).'),
            'keywords': _('Optionally you can add some more specific terms '
                          'to describe your field of research, separated '
                          'by commas.'),
        }

    def save(self, user=None):
        user_profile = super(UserProfileForm, self).save(commit=False)
        if user:
            user_profile.user = user
        user_profile.save()
        return user_profile


class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=True,
        initial=True
    )


class UserCreateForm(CaptchaForm, UserCreationForm):
    username = forms.SlugField(required=True)
    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False

        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'name', 'email',)
        labels = {
            'username': _('User Name'),
            'email': _('Email Address'),
        }
        help_texts = {
            'email': _('We will use this address only when we need to '
                       'communicate with you about this website - it will not '
                       'be displayed to anyone else. It is recommended to enter '
                       'an email address that is not likely to change in the future.'),
        }