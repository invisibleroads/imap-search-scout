# Import system modules
import xapian
import glob
import os
# Import custom modules
from scout import model
from scout.model import meta
from scout.config import parameter
from scout.lib import mail_parse, mail_format


# Index wrapper

class Index(object):

    def __init__(self, pathStore):
        'Connect to xapian database and indexer'
        # Open database
        self.pathStore = pathStore
        self.database = xapian.WritableDatabase(pathStore.getIndexBasePath(), xapian.DB_CREATE_OR_OPEN)
        # Prepare indexer
        self.indexer = xapian.TermGenerator()
        self.indexer.set_stemmer(xapian.Stem('english'))

    def processMessage(self, message, storeMessage, imapAccount, systemAddress):
        # Ignore messages from and to system
        addresses = message['fromWhom'], message['toWhom'], message['ccWhom'], message['bccWhom']
        if systemAddress in ', '.join(filter(lambda x: x, (y.strip() for y in addresses))):
            return False
        # Ignore excluded tags
        message['tags'] = set(map(mail_format.prepareTagText, message['tags']))
        if message['tags'].intersection(map(mail_format.prepareTagText, parameter.EXCLUDED_TAGS)):
            return False
        # Get message
        imapMessage = model.getOldMessage(message['subject'], message['when'])
        # If the message exists,
        if imapMessage:
            isNew = False
        # If the message doesn't exist,
        else:
            # Record message in database
            imapMessage = model.IMAPMessage(imapAccount,
                message['subject'], message['fromWhom'],
                '%s\n%s\n%s' % (message['toWhom'], message['ccWhom'], message['bccWhom']),
                message['when'])
            meta.Session.add(imapMessage)
            meta.Session.commit()
            # Save message in storage and index it
            documentPath = self.pathStore.makeDocumentPath(imapMessage.id)
            storeMessage(message, documentPath)
            self.add(imapMessage)
            isNew = True
        # Try to update the database
        try:
            self.update(imapMessage, imapAccount, message['tags'])
        except xapian.DocNotFoundError:
            # Delete
            model.deleteDocument(self.database, self.pathStore, imapMessage)
        else:
            # Mark
            if imapMessage.message_status < model.message_ok:
                imapMessage.message_status = model.message_ok
        # Return
        return isNew

    def add(self, imapMessage):
        'Add message to xapian database'
        # Initialize
        documentID = imapMessage.id
        documentWhen = imapMessage.when
        documentPath = self.pathStore.fillDocumentPath(documentID)
        # Get header
        headerPath = os.path.join(documentPath, 'header.txt')
        contents = [open(headerPath).read()]
        news = [str(documentID)]
        # Get text
        textPaths = glob.glob(os.path.join(documentPath, 'part*.txt'))
        contents.extend(open(x).read() for x in textPaths)
        if textPaths:
            news.append('%s text' % len(textPaths))
        # If there is no text, get HTML
        else:
            # Initialize
            conversionMethodNames = []
            htmlPaths = glob.glob(os.path.join(documentPath, 'part*.html'))
            # For each htmlPath,
            for htmlPath in htmlPaths:
                # Load html
                html = open(htmlPath).read()
                # Save example
                open(self.pathStore.fillExamplePath(documentID), 'wt').write(html)
                # Convert html to text
                text, conversionMethodName = mail_parse.stripHTML(html)
                # Append
                contents.append(text)
                conversionMethodNames.append(conversionMethodName)
            # Append
            if htmlPaths:
                news.append('%s html (%s)' % (len(htmlPaths), ' '.join(conversionMethodNames)))
        # Get attachment names
        attachmentPacks = model.getRelatedPacks(self.pathStore, documentID)[1]
        attachmentNames = [x[1] for x in attachmentPacks]
        attachmentExtensionTexts = [x[2].lower() for x in attachmentPacks if x[2]]
        contents.append('\n'.join(attachmentNames))
        if attachmentNames:
            news.append('%s attachments' % len(attachmentNames))
        # Assemble content
        content = '\n\n'.join(contents).replace(u'\xa0', ' ').strip()
        print ', '.join(news)
        # Make
        document = xapian.Document()
        document.set_data(mail_format.unicodeSafely(content))
        document.add_value(model.xapian_date, documentWhen.strftime('%Y%m%d%H%M%S'))
        document.add_value(model.xapian_attachmentExtensions, '\n'.join(attachmentExtensionTexts))
        # Index
        self.indexer.set_document(document)
        self.indexer.index_text(content)
        self.database.replace_document(documentID, document)
        # Save attachmentExtensionTexts
        for extensionText in attachmentExtensionTexts:
            attachmentExtension = meta.Session.query(model.AttachmentExtension).filter_by(text=extensionText).first()
            if not attachmentExtension:
                attachmentExtension = model.AttachmentExtension(extensionText)
                meta.Session.add(attachmentExtension)
            imapMessage.attachmentExtensions.append(attachmentExtension)

    def update(self, imapMessage, imapAccount=None, tagTexts=None):
        'Update imapMessage in xapian database'
        # Prepare
        if not imapAccount:
            imapAccount = imapMessage.imap_account
        if not tagTexts:
            tagTexts = [x.text for x in imapMessage.tags]
        # If the current imapAccount is the imapMessage's owner,
        if imapMessage.imap_account == imapAccount:
            # If the message is scheduled for deletion,
            if imapMessage.message_status == model.message_delete:
                # Delete it
                model.deleteDocument(self.database, self.pathStore, imapMessage)
                return
            # Load document
            document = model.Document(self.database, imapMessage.id)
            # Set tags
            imapMessage.setTags(tagTexts)
            document.setTags(tagTexts)
            # Set privacy
            imapMessage.privacy = imapMessage.determinePrivacy()
            document.setPrivacy(imapMessage.privacy)
            # Save
            document.save()

    def flush(self):
        self.database.flush()
