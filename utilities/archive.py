#!/usr/local/bin/python2.6
"""
Archive messages from IMAP
"""
# Import system modules
import sqlalchemy as sa
import xapian
import datetime
# Import custom modules
import script_process
from scout import model
from scout.model import meta
from scout.config import parameter, environment
from scout.lib import imap, mail_process, store


def run(newCountMaximum, includes):
    'Archive messages from IMAP'
    # Initialize
    newCount = 0
    index = mail_process.Index(pathStore)
    # For each imapAccount,
    for imapAccount in meta.Session.query(model.IMAPAccount).filter_by(is_active=True).order_by(sa.func.random()):
        # Connect to imapBox
        try:
            imapBox = imap.Store(imapAccount.host, imapAccount.username, imapAccount.password)
        except imap.IMAPError:
            # Skip accounts to which we cannot connect
            continue
        # For each message in the imapBox,
        for message in imapBox.read(excludes=parameter.EXCLUDED_TAGS, includes=includes):
            # Process
            newCount += index.processMessage(message, storeMessage, imapAccount, systemAddress)
            if newCount >= newCountMaximum:
                return 'Added %s messages; reached maximum for session' % newCount
        # Update
        imapAccount.when_archived = datetime.datetime.utcnow()
    # Return
    return 'Added %s messages' % newCount


def storeMessage(message, documentPath):
    'Save message to hard disk'
    message.save(store.makeFolderSafely(documentPath))


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    optionParser.add_option('-n', '--newCountMaximum', dest='newCountMaximum', help='set the maximum number of new messages', metavar='INTEGER', default=100, type='int')
    options, args = optionParser.parse_args()
    # Initialize
    config, pathStore = script_process.initialize(options)
    extra = environment.loadSensitiveInformation(config.get('app:main', 'extra_path'))
    systemAddress = extra['system']['address']
    # Run
    try:
        print model.clean(pathStore)
        print run(options.newCountMaximum, args)
    except xapian.DatabaseLockError:
        pass
    else:
        meta.Session.commit()
