# Import system modules
import os
import time
import socket
import smtplib
import datetime
import mimetypes
import email.utils
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import email.Encoders


def buildMessage(headerByValue, when=None, bodyText='', bodyHtml='', attachmentPaths=None):
    # Initialize
    if not when:
        when = datetime.datetime.now()
    # Build
    message = email.MIMEMultipart.MIMEMultipart()
    for key, value in headerByValue.iteritems():
        message[key] = value
    message['Date'] = email.utils.formatdate(time.mktime(when.timetuple()), localtime=True)

    # Set body
    mimeText = email.MIMEText.MIMEText(bodyText)
    mimeBody = email.MIMEText.MIMEText(bodyHtml, 'html')
    if bodyText and bodyHtml:
        messageAlternative = email.MIMEMultipart.MIMEMultipart('alternative')
        messageAlternative.attach(mimeText)
        messageAlternative.attach(mimeBody)
        message.attach(messageAlternative)
    elif bodyText:
        message.attach(mimeText)
    elif bodyHtml:
        message.attach(mimeBody)

    # Set attachments
    if attachmentPaths:
        for attachmentPath in attachmentPaths:
            attachmentName = os.path.basename(attachmentPath)
            mimeType = mimetypes.guess_type(attachmentName)[0]
            if not mimeType:
                mimeType = 'application/octet-stream'
            part = email.MIMEBase.MIMEBase(*mimeType.split('/'))
            part.set_payload(open(attachmentPath, 'rb').read())
            email.Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % attachmentName)
            message.attach(part)
    # Return
    return message


def sendMessage(fromByValue, toByValue, subject, body):
    'Send a message using SMTP'
    # Prepare
    message = email.mime.text.MIMEText(body)
    message['To'] = email.utils.formataddr((
        toByValue['nickname'],
        toByValue['email'],
    ))
    message['From'] = email.utils.formataddr((
        fromByValue['nickname'], 
        fromByValue['email'],
    ))
    message['Subject'] = subject
    # Connect to server
    if fromByValue['smtp'] == 'localhost':
        server = smtplib.SMTP('localhost')
    else:
        server = smtplib.SMTP_SSL(fromByValue['smtp'], 465)
        if len(fromByValue['username']):
            server.login(fromByValue['username'], fromByValue['password'])
    # Send mail
    try:
        server.sendmail(fromByValue['email'], toByValue['email'], message.as_string())
    except socket.error, error:
        raise Error(error)
    finally:
        server.quit()


class Error(Exception):
    pass
