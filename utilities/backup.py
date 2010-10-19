#!/usr/local/bin/python2.6


'Backup IMAP messages'


# Import system modules
import shutil
import re
import os
# Import custom modules
import script_process
from scout import model
from scout.model import meta
from scout.lib import mail_format, mail_parse, store


# Core

def run(imapUsername, targetDirectory, isMove=False):
    'Backup messages to hard drive'
    # Initialize
    if not imapUsername:
        return 'Please specify an IMAP username'
    imapAccount = meta.Session.query(model.IMAPAccount.id).filter_by(username=imapUsername).first()
    if not imapAccount: 
        return 'IMAP username "%s" does not exist' % imapUsername
    targetBasePath = os.path.join(targetDirectory, imapUsername)
    if not os.path.exists(targetBasePath):
        store.makeFolderSafely(targetBasePath)
    # Get messageIDs
    messageIDs = [x[0] for x in meta.Session.query(model.IMAPMessage.id).filter(model.IMAPMessage.imap_account_id==imapAccount.id)]
    # For each message,
    for messageID in messageIDs:
        # Get
        sourceDocumentPath = pathStore.fillDocumentPath(messageID)
        targetDocumentPath = os.path.join(targetBasePath, str(messageID))
        # Copy documentPath to targetDocumentPath
        shutil.copytree(sourceDocumentPath, targetDocumentPath)
        if isMove:
            shutil.rmtree(sourceDocumentPath)
        # Load header
        headerPath = os.path.join(targetDocumentPath, 'header.txt')
        message = mail_parse.parseHeader(open(headerPath).read())
        # Define
        pattern_whitespace = re.compile(r'\s+')
        def formatField(fieldName):
            return pattern_whitespace.sub(' ', message[fieldName])
        # Fix header
        when = message['when']
        subject = formatField('subject')
        fromWhom = formatField('fromWhom')
        toWhom = formatField('toWhom')
        ccWhom = formatField('ccWhom')
        bccWhom = formatField('bccWhom')
        # Save
        open(headerPath, 'wt').write(mail_format.formatHeader(subject, when, fromWhom, toWhom, ccWhom, bccWhom))
    # Return
    return 'Saved %s messages' % len(messageIDs)


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    optionParser.add_option('-i', '--imapUsername', dest='imapUsername', help='specifies the source mailbox', metavar='USERNAME', default='')
    optionParser.add_option('-d', '--directory', dest='targetDirectory', help='specifies the target directory', metavar='PATH', default='')
    optionParser.add_option('-m', '--move', dest='isMove', help='move files instead of copying them', action='store_true', default=False)
    options = optionParser.parse_args()[0]
    if options.isMove:
        print 'Moving documents...'
    # Initialize
    pathStore = script_process.initialize(options)[1]
    # Run
    print model.clean(pathStore)
    print run(options.imapUsername, options.targetDirectory, options.isMove)
