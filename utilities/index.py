#!/usr/local/bin/python2.6
"""
Index messages from hard drive
"""
# Import system modules
import shutil
import os
import xapian
# Import custom modules
import script_process
from scout import model
from scout.model import meta
from scout.config import parameter, environment
from scout.lib import mail_format, mail_parse, mail_process


# Core

def run(imapUsername, folderPaths):
    'Index messages from hard drive'
    # Initialize
    if not imapUsername:
        return 'Please specify an IMAP username'
    imapAccount = meta.Session.query(model.IMAPAccount).filter_by(username=imapUsername).first()
    if not imapAccount: 
        return 'IMAP username "%s" does not exist' % imapUsername
    # Initialize
    newCount = 0
    index = mail_process.Index(pathStore)
    # For each folderPath,
    for folderPath in folderPaths:
        # For each subdirectory,
        for subFolderPath in (x[0] for x in os.walk(folderPath)):
            # Skip root
            if subFolderPath == folderPath: 
                continue
            # Define
            def storeMessage(message, documentPath):
                shutil.copytree(subFolderPath, documentPath)
            expandPath = lambda path: os.path.join(subFolderPath, path)
            # Parse header
            message = mail_parse.parseHeader(open(expandPath('header.txt')).read())
            message['tags'] = set(map(mail_format.prepareTagText, open(expandPath('tags.txt')).readlines()))
            # Process
            newCount += index.processMessage(message, storeMessage, imapAccount, systemAddress)
    # Return
    return 'Indexed %s messages' % newCount


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    optionParser.add_option('-i', '--imapUsername', dest='imapUsername', help='specifies the target mailbox', metavar='USERNAME', default='')
    options, arguments = optionParser.parse_args()
    # Initialize
    config, pathStore = script_process.initialize(options)
    extra = environment.loadSensitiveInformation(config.get('app:main', 'extra_path'))
    systemAddress = extra['system']['address']
    # Run
    try:
        print model.clean(pathStore)
        print run(options.imapUsername, arguments)
    except xapian.DatabaseLockError:
        pass
    else:
        meta.Session.commit()
