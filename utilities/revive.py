import os
import sys
from argparse import ArgumentParser
from ConfigParser import ConfigParser, NoSectionError
from formencode import Invalid, Schema
from formencode.validators import Int, String, StringBool
from imapIO import IMAP4, IMAP4_SSL, IMAPError


BASE_PATH = os.path.dirname(__file__)
EXPAND_PATH = lambda x: os.path.join(BASE_PATH, x)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
DESCRIPTION = 'Revive messages from source mailbox to target mailbox'


class ApplicationError(Exception):
    pass


class IMAPForm(Schema):

    host = String
    port = Int
    username = String
    password = String
    ssl = StringBool


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


args = parse_args()
configParser = ConfigParser()
try:
    configParser.read(args.configurationPath)
    configParser.read('.' + args.configurationPath)
except Exception, error:
    print 'Could not parse %s' % args.configurationPath
    print error
    sys.exit(1)
try:
    sourceParameterByKey = load_parameterByKey('source', configParser)
    targetParameterByKey = load_parameterByKey('target', configParser)
except ApplicationError, error:
    print error
    sys.exit(1)
try:
    sourceServer = connect(sourceParameterByKey)
    targetServer = connect(targetParameterByKey)
except IMAPError, error:
    print error
    sys.exit(1)
# Load a message from the source mailbox
# Revive message in target mailbox
