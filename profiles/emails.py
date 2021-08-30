from django.core.mail import EmailMultiAlternatives
from django.template import loader

import main_app.settings as settings


def build_email(subject_template_name, email_template_name, html_email_template_name, context=None):

    subject = loader.render_to_string(subject_template_name, context)
    subject = settings.EMAIL_SUBJECT_PREFIX + ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, settings.EMAIL_FROM, None)
    html_email = loader.render_to_string(html_email_template_name, context)
    email_message.attach_alternative(html_email, 'text/html')

    return email_message


def user_create_confirm_email(
    request, user, uid, token,
    subject_template_name='registration/signup_confirm_email_subject.txt',
    email_template_name='registration/signup_confirm_email_body.txt',
    html_email_template_name='registration/signup_confirm_email_body.html'
):
    context = {
        "request": request,
        "user": user,
        "uid": uid,
        "token": token,
    }

    message = build_email(
        subject_template_name,
        email_template_name,
        html_email_template_name,
        context
    )
    message.to = [user.email]
    return message


def user_reset_password_email(
    request, user, uid, token,
    subject_template_name='registration/reset_password_email_subject.txt',
    email_template_name='registration/reset_password_email_body.txt',
    html_email_template_name='registration/reset_password_email_body.html'
):
    context = {
        "request": request,
        "user": user,
        "uid": uid,
        "token": token,
    }

    message = build_email(
        subject_template_name,
        email_template_name,
        html_email_template_name,
        context
    )
    message.to = [user.email]
    return message