import re
import time
from functools import reduce
from operator import and_, or_

from dal.autocomplete import Select2QuerySetView
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, ModelFormMixin
from django.views.generic.list import ListView
from rest_framework import viewsets

from .emails import user_create_confirm_email, user_reset_password_email
from .forms import (UserCreateForm, UserDeleteForm,
                    UserForm, UserProfileForm)
from .models import Country, Profile, User
from .serializers import CountrySerializer, PositionsCountSerializer


def _to_token(obj, field):
    return urlsafe_base64_encode(force_bytes(getattr(obj, field)))


def _from_token(model, field, data_b64):
    try:
        data = urlsafe_base64_decode(data_b64).decode()
        obj = model.objects.get(**{ field: data })
    except (TypeError, ValueError, OverflowError, ValidationError, AttributeError, model.DoesNotExist):
        obj = None
    return obj


class ListProfiles(ListView):
    template_name = 'profiles/list.html'
    context_object_name = 'profiles'
    model = Profile
    paginate_by = 20

    def get_queryset(self):
        s = self.request.GET.get('s')
        is_underrepresented = self.request.GET.get('ur') == 'on'
        is_senior = self.request.GET.get('senior') == 'on'

        # create filter on search terms
        q_st = ~Q(pk=None)  # always true
        if s is not None:
            # split search terms and filter empty words (if successive spaces)
            search_terms = list(filter(None, s.split(' ')))

            for st in search_terms:
                st_regex = re.compile(f'.*{st}.*', re.IGNORECASE)

                # matching_positions = list(
                #   x[0]
                #   for x in Profile.get_position_choices()
                #   if st_regex.match(x[1]))
                matching_methods = list(
                    Q(methods__contains=x[0])
                    for x
                    in Profile.get_methods_choices()
                    if st_regex.match(x[1]))
                matching_applications = list(
                    Q(applications__contains=x[0])
                    for x
                    in Profile.get_applications_choices()
                    if st_regex.match(x[1]))

                st_conditions = [
                    Q(name__icontains=st),
                    Q(institution__icontains=st),
                    Q(position__icontains=st),
                    Q(country__name__icontains=st),
                    Q(keywords__icontains=st),
                 ] + matching_methods \
                   + matching_applications

                q_st = and_(reduce(or_, st_conditions), q_st)

        #  create filter on under-represented countries
        if is_underrepresented:
            q_ur = Q(country__is_under_represented=True)
        else:
            q_ur = ~Q(pk=None)  # always true

        # create filter on senior profiles
        if is_senior:
            senior_profiles_keywords = ('Senior', 'Lecturer', 'Professor',
                                        'Director')
            # position must contain one of the words(case insensitive)
            q_senior = reduce(or_, (Q(position__icontains=x)
                                    for x
                                    in senior_profiles_keywords))
        else:
            q_senior = ~Q(pk=None)  # always true

        # apply filters
        profiles_list = Profile.objects \
                               .filter(q_st, q_ur, q_senior) \
                               .order_by('-publish_date')

        return profiles_list


class ProfileDetail(DetailView):
    model = Profile


class UserProfileView(TemplateView):
    template_name = "account/user_profile.html"


class UserProfileEditView(SuccessMessageMixin, ModelFormMixin, FormView):
    template_name = "account/user_profile_form.html"
    form_class = UserProfileForm
    success_message = 'Your profile has been saved successfully!'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.request.user.profile
        except Profile.DoesNotExist:
            self.object = Profile()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.request.user.profile
        except Profile.DoesNotExist:
            self.object = Profile()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:user_profile')


class UserView(LoginRequiredMixin, TemplateView):
    template_name = "account/user.html"


class UserEditView(LoginRequiredMixin, SuccessMessageMixin, ModelFormMixin, FormView):
    template_name = "account/user_form.html"
    form_class = UserForm
    success_message = 'Your account has been updated successfully!'

    def get(self, request, *args, **kwargs):
        self.object = self.request.user
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.request.user
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:user')


class UserChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    form_class = PasswordChangeForm
    template_name = "account/user_change_password.html"
    success_message = 'Your password has been updated successfully!'


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:user')


class UserDeleteView(LoginRequiredMixin, FormView):
    form_class = UserDeleteForm
    template_name = 'account/user_delete.html'
    success_message = 'Your account has been deleted successfully!'

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        user = _from_token(User, 'email', uid)
        if token and user is not None:
            if self.token_generator.check_token(user, token):
                user.is_active = True
                if Profile.objects.filter(contact_email=user.email).exists():
                    user.profile = Profile.objects.get(contact_email=user.email)
                user.save()

            messages.success(self.request, self.success_message)
            return redirect('profiles:login')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user

        logout(self.request)

        try:
            profile = user.profile
            profile.delete()
        except Profile.DoesNotExist:
            pass

        user.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:login')


class UserCreateView(CreateView):
    form_class = UserCreateForm
    template_name = 'registration/signup.html'
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profiles:user')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        valid = super().form_valid(form)
        uid =_to_token(self.object, 'email')
        token = self.token_generator.make_token(self.object)
        user_create_confirm_email(self.request, self.object, uid, token).send()
        return valid

    def get_success_url(self):
        return reverse('profiles:signup_confirm')


class UserCreateConfirmView(TemplateView):
    template_name = 'registration/signup_confirm.html'
    success_message = 'Your account has been activated successfully. Please, log-in!'
    error_message = 'There was an error with your activation. Please, try again.'

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        user = _from_token(User, 'email', uid)
        if token and user is not None:
            if self.token_generator.check_token(user, token):
                user.is_active = True

                messages.success(self.request, self.success_message)
            else:
                messages.error(self.request, self.error_message)
            # return redirect('profiles:login')

        return super().get(request, *args, **kwargs)


class UserPasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'registration/reset_password.html'
    token_generator = default_token_generator
    success_message = 'Please check your email address for directions on how to reset your password.'
    error_message = 'This email is not linked to a WiML account.'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profiles:user')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            uid =_to_token(user, 'email')
            token = self.token_generator.make_token(user)
            user_reset_password_email(self.request, user, uid, token).send()
        except User.DoesNotExist:
            messages.error(self.request, self.error_message)

        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:forgot')


class UserPasswordResetConfirmView(FormView):
    form_class = SetPasswordForm
    template_name = 'registration/reset_password_confirm.html'
    success_message = 'Your password has been reset. Please, log-in!'
    error_message = 'There was an error with your password reset. Please, try again.'

    token_generator = default_token_generator

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        user = _from_token(User, 'email', uid)

        self.user = None
        if token and user is not None:
            if self.token_generator.check_token(user, token):
                self.user = user

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.user:
            return super().get(request, *args, **kwargs)

        messages.error(self.request, self.error_message)
        return redirect('profiles:forgot')

    def form_valid(self, form):
        form.user.is_active = True
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('profiles:login')


class ProfilesAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        profiles = Profile.objects.all()

        # If search terms in request, split each word and search for them
        # in name & institution
        if self.q:
            qs = ~Q(pk=None)  # always true
            search_terms = list(filter(None, self.q.split(' ')))
            for st in search_terms:
                qs = and_(or_(Q(name__icontains=st),
                              Q(institution__icontains=st)), qs)

            profiles = profiles.filter(qs)

        return profiles


class CountriesAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        countries = Country.objects.all()

        # If search terms in request, split each word and search for them
        # in name & institution
        if self.q:
            qs = ~Q(pk=None)  # always true
            search_terms = list(filter(None, self.q.split(' ')))
            for st in search_terms:
                qs = and_(Q(name__icontains=st), qs)

            countries = countries.filter(qs)

        return countries


class RepresentedCountriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.annotate(profiles_count=Count('profiles')) \
                              .filter(profiles_count__gt=0)
    serializer_class = CountrySerializer
    authentication_classes = []


class TopPositionsViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []

    queryset = Profile.objects.all() \
        .values('position') \
        .annotate(profiles_count=Count('id')) \
        .order_by('-profiles_count')
    serializer_class = PositionsCountSerializer
