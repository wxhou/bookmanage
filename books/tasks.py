from __future__ import absolute_import, unicode_literals
from flask_mail import Message
from server import book_manage_celery as celery
from app.extensions import mail


@celery.task
def send_register_email(register_url, email):
    message = Message(subject="激活链接",
                      recipients=[email],
                      html="""
        <p>New User is register, click the link to check:</p>
        <p><a href="%s">%s</a></P>        
        <p><small style="color: #868e96">Do not reply this email.</small></p>
        """ % (register_url, register_url))
    mail.send(message)
