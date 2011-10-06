import re
import os
import sys
import socket
import logging
import datetime
from argparse import ArgumentParser
from calendar import timegm
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from email.utils import mktime_tz, parseaddr, parsedate_tz
from formencode import Invalid, Schema, validators
from imapIO import IMAP4, IMAP4_SSL, IMAPError
from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


BASE_PATH = os.path.dirname(__file__)
EXPAND_PATH = lambda x: os.path.join(BASE_PATH, x)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
DESCRIPTION = 'Revive messages from source mailbox to target mailbox'
RAW_FROM_LEN_MAX = 32
RAW_DATE_LEN_MAX = 32
SOCKET = socket.socket()
PATTERN_PORT = re.compile(r'(\d+)')


Base = declarative_base()
Session = sessionmaker()
db = Session()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    raw_from = Column(String(RAW_FROM_LEN_MAX))
    raw_date = Column(String(RAW_DATE_LEN_MAX))
    date = Column(Date)


class ApplicationError(Exception):
    pass


class IMAPForm(Schema):

    host = validators.String
    port = validators.Int
    username = validators.String
    password = validators.String
    ssl = validators.StringBool


def parse_args():
    argumentParser = ArgumentParser(description=DESCRIPTION)
    argumentParser.add_argument('-c',
        default=EXPAND_PATH(SCRIPT_NAME) + '.ini',
        dest='configurationPath', 
        help='use the specified configuration file',
        metavar='PATH')
    argumentParser.add_argument('-q',
        action='store_false',
        default=True,
        dest='verbose',
        help='be quiet')
    argumentParser.add_argument('-f',
        action='store_false',
        default=True,
        dest='incremental',
        help='ignore last scan time and scan source mailbox fully')
    return argumentParser.parse_args()


def load_parameterByKey(section, configParser):
    try:
        parameterByKey = dict(configParser.items(section))
    except NoSectionError:
        raise ApplicationError('Configuration is missing section: %s' % section)
    try:
        parameterByKey = IMAPForm().to_python(parameterByKey)
    except Invalid, error:
        lines = ['Error parsing section: %s' % section]
        for key, value in error.unpack_errors().iteritems():
            lines.append('%s: %s' % (key, value))
        raise ApplicationError('\n'.join(lines))
    return parameterByKey


def connect(parameterByKey):
    IMAPClass = IMAP4_SSL if parameterByKey['ssl'] else IMAP4
    return IMAPClass.connect(
        parameterByKey['host'], 
        parameterByKey['port'], 
        parameterByKey['username'], 
        parameterByKey['password'])


def parse_port(portString):
    'Convert string to integer while ignoring other text such as comments'
    match = PATTERN_PORT.search(portString)
    try:
        return int(match.group(1))
    except AttributeError:
        raise ValueError('Could not parse port=%s' % portString)


def parse_whenLocal(message):
    timePack = parsedate_tz(message['date'])
    if not timePack:
        return
    timeStamp = timegm(timePack) if timePack[-1] is None else mktime_tz(timePack)
    return datetime.datetime.fromtimestamp(timeStamp)


def has(server, message):
    'Return True if the IMAP server has a copy of the message'
    messageFrom = message['fromWhom']
    messageDate = message['date']
    whenLocal = parse_whenLocal(message)
    # Without a date, I cannot easily test for duplicates
    if not whenLocal:
        return False
    excludes = filter(lambda x: x.startswith('"[Gmail]'), revive.targetServer.folders) # Exclude virtual Gmail folders
    searchCriterion = 'FROM "%s" SENTON "%s"' % (parseaddr(messageFrom)[1], whenLocal.strftime('%d-%b-%Y'))
    messageGenerator = server.walk(excludes=excludes, searchCriterion=searchCriterion)
    for m in messageGenerator:
        if m['date'] == messageDate:
            return True
    return False


def has_record(message):
    'Return True if we have already have a record of this message'
    result = db.query(Message.id).filter(
        (Message.raw_from==message['fromWhom'][:RAW_FROM_LEN_MAX]) &
        (Message.raw_date==message['date'][:RAW_DATE_LEN_MAX])).first()
    return True if result else False


def record(message):
    'Record the message in our database'
    db.add(Message(
        raw_from=message['fromWhom'][:RAW_FROM_LEN_MAX], 
        raw_date=message['date'][:RAW_DATE_LEN_MAX],
        date=parse_whenLocal(message).date()))
    db.commit()


# Parse arguments and load configuration file
args = parse_args()
configParser = ConfigParser()
try:
    configParser.read(args.configurationPath)
    configParser.read('.' + args.configurationPath)
except Exception, error:
    print 'Could not parse %s' % args.configurationPath
    print error
    sys.exit(1)
def send_feedback(x):
    if args.verbose:
        print x
# Make sure only one instance of this script is running
section, portlock = 'app:portlock', 'revive'
try:
    portString = configParser.get(section, portlock)
except (NoSectionError, NoOptionError):
    print ('To ensure that only one instance of this script is running, '
            "specify a unique port number for '%s' in '%s'" % (portlock, section))
else:
    port = parse_port(portString)
    try:
        SOCKET.bind(('', port))
    except socket.error:
        sys.exit(1)
# Connect to IMAP servers
log = logging.getLogger('imapIO')
log.addHandler(logging.StreamHandler())
try:
    sourceParameterByKey = load_parameterByKey('source', configParser)
    targetParameterByKey = load_parameterByKey('target', configParser)
except ApplicationError, error:
    print error
    sys.exit(1)
try:
    send_feedback('Connecting to source server')
    sourceServer = connect(sourceParameterByKey)
    send_feedback('Connecting to target server')
    targetServer = connect(targetParameterByKey)
except IMAPError, error:
    print error
    sys.exit(1)
# Prepare database
engine = create_engine('sqlite:///%(username)s@%(host)s.db' % sourceParameterByKey)
db.configure(bind=engine)
Base.metadata.bind = engine
Base.metadata.create_all(engine)
# Get most recent scan date
if args.incremental:
    result = db.query(Message.date).order_by(Message.date.desc()).first()
    searchCriterion = 'SINCE %s' % result[0].strftime('%d-%b-%Y') if result else ''
    send_feedback(searchCriterion)
else:
    searchCriterion = ''
# Load a message from the source mailbox
for email in sourceServer.walk(searchCriterion=searchCriterion):
    # If we already have a record of this email,
    if has_record(email):
        continue
    # If the message does not exist in the target mailbox,
    if not has(targetServer, email):
        send_feedback(email['subject'].encode('utf-8'))
        # Revive message in target mailbox
        targetServer.revive(email.folder, email)
        # Record email in our local database
        record(email)
