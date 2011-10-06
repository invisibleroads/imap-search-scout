'Export database to external IMAP server'
import imapIO
import socket

import script_process
from scout import model
from scout.model import meta


SOCKET = socket.socket()


if __name__ == '__main__':
    configParser = ConfigParser()
    configParser.read('.export.ini')
    sourceUsername = configParser.get('app:scout', 'username')
    targetIMAPHost = configParser.get('target', 'host')
    targetIMAPPort = configParser.get('target', 'host')
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
