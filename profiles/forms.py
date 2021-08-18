from django import forms
from django.utils.translation import gettext_lazy as _

from captcha.fields import ReCaptchaField
from dal.autocomplete import ModelSelect2
from captcha.widgets import ReCaptchaV3

from .models import Profile


class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label=False)


class CreateProfileModelForm(CaptchaForm, forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Profile
        fields = [
            'name',
            'institution',
            'country',
            'email',
            'webpage',
            'position',
            'grad_month',
            'grad_year',
            'brain_structure',
            'modalities',
            'methods',
            'domains',
            'keywords',
        ]
        labels = {
            'name': _('Full Name'),
            'institution': _('Institution/Company'),
            'email': _('Email Address'),
            'webpage': _('Linked In or web page'),
            'grad_month': _('Date PhD was obtained: Month'),
            'grad_year': _('Year'),
            'brain_structure': _('Field of Research - Brain Structure'),
            'modalities': _('Field of Research - Modalities'),
            'methods': _('Field of Research - Methods'),
            'domains': _('Field of Research - Domain'),
            'keywords': _('Field of Research - Keywords'),
        }
        help_texts = {
            'country': _('Country of the institution'),
            'webpage': _('Make sure people can look you up easily by '
                         'providing a link to a personal website, profile '
                         'or institution site.'),
            'position': _('Please choose your \'highest\' title from the '
                          'proposed options to ease future searches.'),
            'grad_month': _('Leave empty if no PhD (yet).'),
            'grad_year': _('Please enter the full year (4 digits).'),
            'domains': _('There are free keywords at the end of the '
                         'questionnaire to input further information.'),
            'keywords': _('Optionally you can add some more specific terms '
                          'to describe your field of research, separated '
                          'by commas.'),
        }
        widgets = {
            'country': ModelSelect2(
                url='profiles:countries_autocomplete',
                attrs={
                    # 'data-minimum-input-length': 2,
                    'data-placeholder': 'Search Country...',
                },
            )
        }

    def clean_email(self):
        email = self.cleaned_data['email']

        if email and Profile.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already being used'),
                                        code='duplicate_email')

        return email