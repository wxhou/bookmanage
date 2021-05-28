from threading import Thread
from flask import current_app, url_for
from flask_mail import Message
from .extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to: list, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=to, html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_register_email(token, email):
    register_url = url_for('.active_user', token=token, _external=True)
    send_mail(subject="激活链接",
              to=[email],
              html="""
        <p>New User is register, click the link to check:</p>
        <p><a href="%s">%s</a></P>        
        <p><small style="color: #868e96">Do not reply this email.</small></p>
        """ % (register_url, register_url))
