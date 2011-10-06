'Export database to external IMAP server'
import os
import sys
import socket
import imapIO
import datetime
from email.utils import mktime_tz, parseaddr, parsedate_tz
from imaplib import IMAP4_SSL
from ConfigParser import ConfigParser

import script_process
from scout import model
from scout.lib import mail, mail_parse, mail_store_imap
from scout.model import meta


class IMAPStore(mail_store_imap.Store):
    'IMAP4 interface'

    # Connection

    def __init__(self, mailHost, mailName, mailPassword):
        self.server = IMAP4_SSL(mailHost)
        self.server.login(mailName, mailPassword)
        self.mailHost = mailHost
        self.mailName = mailName


def parse_whenLocal(message):
    timePack = parsedate_tz(message['date'])
    if not timePack:
        return
    timeStamp = timegm(timePack) if timePack[-1] is None else mktime_tz(timePack)
    return datetime.datetime.fromtimestamp(timeStamp)


def has(server, message):
    'Return True if the IMAP server has a copy of the message'
    messageFrom = message['from']
    messageDate = message['date']
    whenLocal = parse_whenLocal(message)
    # Without a date, I cannot easily test for duplicates
    if not whenLocal:
        return False
    excludes = filter(lambda x: x.startswith('"[Gmail]'), server.folders) # Exclude virtual Gmail folders
    searchCriterion = 'FROM "%s" SENTON "%s"' % (parseaddr(messageFrom)[1], whenLocal.strftime('%d-%b-%Y'))
    messageGenerator = server.walk(excludes=excludes, searchCriterion=searchCriterion)
    for m in messageGenerator:
        if m['date'] == messageDate:
            return True
    return False


SOCKET = socket.socket()
DB = meta.Session


configParser = ConfigParser()
configParser.read('.export.ini')
sourceUsername = configParser.get('app:scout', 'username')
targetIMAPHost = configParser.get('target', 'host')
targetIMAPPort = configParser.get('target', 'port')
targetIMAPUsername = configParser.get('target', 'username')
targetIMAPPassword = configParser.get('target', 'password')
port = int(configParser.get('app:portlock', 'export'))
try:
    SOCKET.bind(('', port))
except socket.error:
    sys.exit(1)
optionParser = script_process.buildOptionParser()
options, args = optionParser.parse_args()
pathStore = script_process.initialize(options)[1]


startID = int(open('export.log', 'rt').read().strip())


personID = DB.query(model.Person.id).filter_by(username=sourceUsername).first()[0]
messageQuery = DB.query(model.IMAPMessage.id).filter(model.IMAPMessage.id >= startID).filter((model.IMAPMessage.privacy==0) | (model.IMAPMessage.privacy==personID)).order_by(model.IMAPMessage.id)


imapStore = IMAPStore(targetIMAPHost, targetIMAPUsername, targetIMAPPassword)
imapServer = imapIO.connect(targetIMAPHost, targetIMAPPort, targetIMAPUsername, targetIMAPPassword)


for result in messageQuery:

    documentID = result[0]
    documentPath = pathStore.fillDocumentPath(documentID)
    tagsPath = os.path.join(documentPath, 'tags.txt')
    tags = [x.strip() for x in open(tagsPath)]
    # targetFolder = ' '.join(tags)
    headerPath = os.path.join(documentPath, 'header.txt')
    headerByName = mail_parse.parseHeader(open(headerPath).read())

    partPacks, attachmentPacks = model.getRelatedPacks(pathStore, documentID)
    bodyTexts, bodyHtmls = [], []
    for fileNumber, partName, partExtension in partPacks:
        partContent = open(os.path.join(documentPath, partName)).read()
        if partExtension == 'txt':
            bodyTexts.append(partContent)
        else:
            bodyHtmls.append(partContent)


    message = mail.buildMessage(
        {
            'From': headerByName['fromWhom'],
            'To': headerByName['toWhom'],
            'CC': headerByName['ccWhom'],
            'BCC': headerByName['bccWhom'],
            'Subject': headerByName['subject'],
        },  
        when=headerByName['when'],
        bodyText='\n\n'.join(bodyTexts),
        bodyHtml='<br><br>'.join(bodyHtmls),
        attachmentPaths=[os.path.join(documentPath, x[1]) for x in attachmentPacks])   


    print documentID, message['subject'].encode('utf-8'),
    if has(imapServer, message):
        print '[exists]'
    else:
        code, status = imapStore.revive('inbox', message, headerByName['when'])
        if code.lower() == 'no':
            raise Exception(status)
        print '[ok]'
        # assert has(imapServer, message) == True
    open('export.log', 'wt').write(str(documentID))
