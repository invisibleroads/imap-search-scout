'Helpers'
# Import pylons modules
from pylons import session, request, url
# Import system modules
from webhelpers.util import html_escape
from webhelpers.html import literal
from webhelpers.html.tags import *
# Import custom modules
from scout.config.parameter import *
from scout.lib import whenIO


def encodeURL(x):
    return x.replace('/', '~')

def decodeURL(x):
    return str(x.replace('~', '/'))

def isPerson():
    return 1 if 'personID' in session else 0

def isPersonSuper():
    return 'personID' in session and session['is_super']

def clipString(string, characterLimit=32):
    return string[:characterLimit] + '...' if len(string) > characterLimit else string

def getPersonID():
    return session.get('personID', 0)

def getMinutesOffset():
    try:
        return int(request.params.get('minutesOffset', session.get('minutesOffset', MINUTES_OFFSET_DEFAULT)))
    except ValueError:
        return MINUTES_OFFSET_DEFAULT

def getWhenIO():
    return whenIO.WhenIO(getMinutesOffset())

def getRemoteIP():
    return request.environ.get('HTTP_X_REAL_IP', 
           request.environ.get('HTTP_X_FORWARDED_FOR', 
           request.environ.get('REMOTE_ADDR')))