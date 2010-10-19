# Import system modules
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.append(basePath)
import win32com.client
import pywintypes
import datetime
import optparse
import time
# Import custom modules
from scout.lib import mail_format
from scout.lib import view


class Scribe(object):

    def __init__(self, storagePath='.', messageIndex=1):
        self.storagePath = storagePath
        self.messageIndex = messageIndex

    def saveFolders(self, folders, parentTags):
        # Convert Microsoft array
        try:
            folders[0]
        except pywintypes.com_error:
            folders = [folders[x] for x in xrange(1, len(folders) + 1)]
        # For each folder,
        for folder in folders:
            # Get
            items = folder.Items
            childTags = parentTags + [folder.Name]
            print 'Folder:\t' + '\n\t'.join(childTags)
            # For each item,
            for itemIndex in xrange(1, len(items) + 1):
                # Add delay
                if itemIndex % 100 == 0:
                    time.sleep(1)
                # Get
                item = items[itemIndex]
                # If we have a MailItem,
                if 'MailItem' in str(item):
                    # Show feedback
                    # print item.Subject
                    # Ignore drafts
                    try:
                        when = datetime.datetime.fromtimestamp(int(item.SentOn)) 
                    except ValueError:
                        continue
                    # Prepare itemFolder
                    itemFolder = os.path.join(self.storagePath, str(self.messageIndex))
                    os.mkdir(itemFolder)
                    # Prepare recipients
                    recipients = item.Recipients
                    tos = []; ccs = []; bccs = []
                    for recipientIndex in xrange(1, len(recipients) + 1):
                        recipient = recipients[recipientIndex]
                        recipientString = '%s <%s>' % (recipient.Name, recipient.Address)
                        if recipient.Type == win32com.client.constants.olTo: tos.append(recipientString)
                        elif recipient.Type == win32com.client.constants.olCC: ccs.append(recipientString)
                        elif recipient.Type == win32com.client.constants.olBCC: bccs.append(recipientString)
                    # Save header
                    open(os.path.join(itemFolder, 'header.txt'), 'wt').write(mail_format.formatHeader(item.Subject, when, item.SenderEmailAddress, ', '.join(tos), ', '.join(ccs), ', '.join(bccs)))
                    partIndex = 1
                    try:
                        # Save text
                        open(os.path.join(itemFolder, 'part%03i.txt' % partIndex), 'wt').write(mail_format.unicodeSafely(item.Body))
                        partIndex += 1
                    except:
                        pass
                    try:
                        # Save html
                        open(os.path.join(itemFolder, 'part%03i.html' % partIndex), 'wt').write(mail_format.unicodeSafely(item.HTMLBody))
                        partIndex += 1
                    except:
                        pass
                    # Save tag
                    tagPath = os.path.join(itemFolder, 'tags.txt')
                    open(tagPath, 'wt').write('\n'.join(childTags))
                    # Prepare attachments
                    attachments = item.Attachments
                    for attachmentIndex in xrange(1, len(attachments) + 1):
                        # Get
                        attachment = attachments[attachmentIndex]
                        attachmentName = mail_format.sanitizeFileName(attachment.FileName)
                        # Save
                        attachmentPath = os.path.abspath(os.path.join(itemFolder, attachmentName))
                        attachment.SaveAsFile(attachmentPath[:256])
                    # Increment
                    self.messageIndex += 1
                    # Show feedback
                    view.printPercentUpdate(itemIndex, len(items))
            view.printPercentFinal(len(items))
            # Recurse
            self.saveFolders(folder.Folders, childTags)

    def getStoragePath(self):
        return self.storagePath


if __name__ == '__main__':
    # Connect
    application = win32com.client.Dispatch('Outlook.Application')
    namespace = application.GetNamespace('MAPI')
    folders = namespace.Folders
    try:
        folders[0]
    except pywintypes.com_error:
        pass
    else:
        print 'Please run makepy on Microsoft Office 11 Object Library'
        print 'Please run makepy on Microsoft Outlook 11 Object Library'
        sys.exit(-1)
    folderRange = xrange(1, len(folders) + 1)
    # Parse
    parser = optparse.OptionParser()
    options, arguments = parser.parse_args()
    # Act
    if arguments:
        command = arguments.pop(0)
        if command == 'see':
            for folderIndex in folderRange:
                print folders[folderIndex].Name
        elif command == 'mirror':
            # Filter
            folders = filter(lambda x: x.Name in arguments, (folders[x] for x in folderRange))
            if folders:
                # Prepare
                storagePath = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                os.mkdir(storagePath)
                # Download
                scribe = Scribe(storagePath)
                scribe.saveFolders(folders, [])
    else:
        print 'see'
        print 'mirror folder1 folder2 ...'
