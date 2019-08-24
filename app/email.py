from flask_mail import Message
from flask import render_template, current_app
from app import mail, celery
import json

@celery.task
def send_async_email(msgd):
    """Background task to send an email with Flask-Mail."""
    msg = Message(subject=msgd['subject'],recipients=msgd['recipients'],body=msgd['body'],html=msgd['html'],sender=msgd['sender'],
    cc=msgd['cc'], bcc=msgd['bcc'])
    mail.send(msg)
    

def send_email(subject, sender, recipients, text_body, html_body=None, cc=None, bcc=None):
    msgd = {'recipients': recipients, 'subject': subject, 'body': text_body, 'html': html_body, 'sender': sender, 'cc': cc, 'bcc': bcc}
    send_async_email.delay(msgd)