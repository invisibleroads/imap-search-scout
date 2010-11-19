# Import pylons modules
from pylons import request, response, session, tmpl_context as c, config
from pylons.controllers.util import abort, redirect_to, forward
from pylons.decorators import jsonify
from paste.fileapp import FileApp
# Import system modules
import logging; log = logging.getLogger(__name__)
import xapian
import os
import simplejson
# Import custom modules
from scout.lib.base import BaseController, render
from scout.lib import mail, imap, mail_parse
from scout.lib import file_store, query_process
from scout.lib import helpers as h
from scout.config import parameter
from scout.model import meta
from scout import model


# Set paths
pathStore = file_store.PathStore(config['path_storage'])


class MailController(BaseController):

    withAuthentication = True

    def index(self):
        """
        Display the search interface with some help and options 
        for browsing through the archive.
        """
        # Initialize
        messageTagID = request.GET.get('messageTagID', 'any')
        attachmentExtensionID = request.GET.get('attachmentExtensionID', 'can')
        # Prepare
        query = meta.Session.query(model.IMAPMessage).filter((model.IMAPMessage.privacy==0) | (model.IMAPMessage.privacy == session['personID'])).filter(model.IMAPMessage.message_status!=model.message_incomplete)
        if messageTagID != 'any':
            query = query.join(model.IMAPMessage.tags).filter(model.IMAPMessageTag.id==messageTagID)
        if attachmentExtensionID == 'must':
            query = query.filter(model.IMAPMessage.attachmentExtensions.any())
        elif attachmentExtensionID != 'can':
            query = query.join(model.IMAPMessage.attachmentExtensions).filter(model.AttachmentExtension.id==attachmentExtensionID)
        # Fill
        c.totalCount = query.count()
        c.startIndex = adjustStartIndex(request.GET.get('startIndex', 0), c.totalCount)
        c.imapAccounts = meta.Session.query(model.IMAPAccount).filter_by(owner_id=session['personID']).all()
        c.attachmentExtensions = meta.Session.query(model.AttachmentExtension).order_by(model.AttachmentExtension.text).all()
        c.messageTags = meta.Session.query(model.IMAPMessageTag).order_by(model.IMAPMessageTag.text).all()
        # Get
        imapMessages = query.order_by(model.IMAPMessage.when.desc()).limit(10).offset(c.startIndex).all()
        # If we have messages,
        if imapMessages:
            c.matches, c.highlight = buildMatches(imapMessages)
        # Return
        if request.GET.get('format', 'html') == 'html':
            return render('/emails/index.mako')
        else:
            return simplejson.dumps({
                'payload': render('/emails/payload.mako'),
                'pagination': render('/emails/pagination.mako'),
                'startIndex': c.startIndex,
            })

    @jsonify
    def search(self):
        # Get
        queryString = request.GET.get('q', '')
        totalCount = request.GET.get('totalCount', 0)
        c.startIndex = adjustStartIndex(request.GET.get('startIndex', 0), totalCount)
        sortBy = request.GET.get('sortBy', 'relevance')
        messageTagID = request.GET.get('messageTagID', 'any')
        attachmentExtensionID = request.GET.get('attachmentExtensionID', 'can')
        # If there is one or fewer terms in the query,
        if len(queryString.split()) <= 1:
            # Sort results by date
            sortBy = 'date'
        # Open database
        try:
            database = xapian.Database(pathStore.getIndexBasePath())
        except xapian.DatabaseOpeningError:
            return {'isOk': 0, 'message': 'Could not open Xapian database'}
        # Parse query string
        queryParser = query_process.getQueryParser()
        queryParser.set_database(database)
        query = queryParser.parse_query(queryString)
        # Start query session
        enquire = xapian.Enquire(database)
        if sortBy == 'date':
            enquire.set_sort_by_value(model.xapian_date)
        enquire.set_query(query)
        matchDecider = MatchDecider(session['personID'], messageTagID, attachmentExtensionID)
        matches = enquire.get_mset(c.startIndex, parameter.RESULTS_PER_PAGE, None, matchDecider)
        matchesByID = dict((x.docid, x) for x in matches)
        imapMessages = meta.Session.query(model.IMAPMessage).filter(model.IMAPMessage.id.in_(matchesByID.keys())).filter(model.IMAPMessage.message_status!=model.message_incomplete).order_by(model.IMAPMessage.when.desc())
        # Set
        c.matches, c.highlight = buildMatches(imapMessages, queryString)
        c.totalCount = matches.get_matches_estimated()
        # Return
        return {
            'isOk': 1,
            'sortBy': sortBy,
            'payload': render('/emails/payload.mako'),
            'pagination': render('/emails/pagination.mako'),
            'startIndex': c.startIndex,
            'totalCount': c.totalCount,
        }

    def download(self, documentID, fileNumber):
        # Verify access
        try:
            verifyAccess(documentID, session['personID'])
        except AccessError, error:
            return str(error)
        # Load related paths
        relatedPaths = model.getRelatedPaths(pathStore, documentID)
        # Make sure the file exists
        try:
            filePath = relatedPaths[int(fileNumber)]
        except (ValueError, IndexError):
            return 'File does not exist'
        # Return
        fileApp = FileApp(filePath)
        fileApp.content_disposition(filename=os.path.basename(filePath))
        return forward(fileApp)

    @jsonify
    def revive(self, documentID=0):
        # Verify
        try:
            verifyAccess(documentID, session['personID'])
        except AccessError, error:
            return {'isOk': 0, 'message': str(error)}
        # See if the user has picked an imapAccount
        try:
            whichAccount = int(request.POST.get('whichAccount', 0))
        except ValueError:
            return {'isOk': 0, 'message': 'The whichAccount variable must be an integer.'}
        # Get imapAccounts for user
        imapAccounts = meta.Session.query(model.IMAPAccount).filter_by(owner_id=session['personID']).all()
        # If the user has no imapAccounts,
        if not imapAccounts:
            return {'isOk': 0, 'message': 'You have no email addresses defined for your account.\nPlease link an email address on the Accounts page.'}
        # Choose IMAP account
        try:
            imapAccount = imapAccounts[whichAccount]
        except IndexError:
            return {'isOk': 0, 'message': 'The whichAccount variable does not correspond to an actual account.'}
        # Connect to the IMAP account
        try:
            imapStore = imap.Store(imapAccount.host, imapAccount.username, imapAccount.password)
        except imap.IMAPError:
            return {'isOk': 0, 'message': 'Cannot connect to IMAP account.\nPlease check your IMAP password on the Accounts page.'}
        # Parse header
        documentPath = pathStore.fillDocumentPath(documentID)
        headerPath = os.path.join(documentPath, 'header.txt')
        headerByName = mail_parse.parseHeader(open(headerPath).read())
        # Get
        partPacks, attachmentPacks = model.getRelatedPacks(pathStore, documentID)
        bodyTexts, bodyHtmls = [], []
        for fileNumber, partName, partExtension in partPacks:
            partContent = open(os.path.join(documentPath, partName)).read()
            if partExtension == 'txt':
                bodyTexts.append(partContent)
            else:
                bodyHtmls.append(partContent)
        # Revive
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
            attachmentPaths=[os.path.join(documentPath, x[1]) for x in attachmentPacks],
        )
        code, message = imapStore.revive(parameter.FOLDER_REVIVED, message, headerByName['when'])
        # Return
        return {
            'isOk': code != 'NO',
            'message': message,
            'folder': parameter.FOLDER_REVIVED,
            'email': '%s@%s' % (imapAccount.username, imapAccount.host),
        }

    @jsonify
    def change(self, documentID=0):
        # Verify
        try:
            verifyAccess(documentID, session['personID'])
        except AccessError, error:
            return {'isOk': 0, 'message': str(error)}
        # Get status
        try:
            status = int(request.POST.get('status', model.message_ok))
        except ValueError:
            return {'isOk': 0, 'message': 'The status must be an integer'}
        # Load imapMessage and set status
        imapMessage = meta.Session.query(model.IMAPMessage).get(documentID)
        imapMessage.message_status = status
        imapMessage.message_status_changed = True
        meta.Session.commit()
        # Prepare
        valueByName = {'isOk': 1}
        if status != model.message_delete:
            valueByName['privacy'] = imapMessage.determinePrivacy()
        # Return
        return valueByName

    @jsonify
    def get(self, documentID=0):
        # Verify
        try:
            verifyAccess(documentID, session['personID'])
        except AccessError, error:
            return {'isOk': 0, 'message': str(error)}
        # Open database
        try:
            database = xapian.Database(pathStore.getIndexBasePath())
        except xapian.DatabaseOpeningError:
            return {'isOk': 0, 'message': 'Could not open Xapian database'}
        # Load imapMessage
        imapMessage = meta.Session.query(model.IMAPMessage).get(documentID)
        document = model.Document(database, imapMessage.id)
        # Return
        return {
            'isOk': 1,
            'from_whom': imapMessage.from_whom,
            'subject': imapMessage.subject,
            'body': document.getContent(),
        }


class AccessError(Exception):
    pass


def verifyAccess(documentID, personID):
    # If we can't access the message,
    if not meta.Session.query(model.IMAPMessage.id).filter(model.IMAPMessage.id==documentID).filter((model.IMAPMessage.privacy==0) | (model.IMAPMessage.privacy==personID)).first():
        # Raise exception
        raise AccessError('Could not open this document')


def buildMatches(imapMessages, queryString=''):
    # Initialize
    database = xapian.Database(pathStore.getIndexBasePath())
    matches = []
    # For each imapMessage,
    for imapMessage in imapMessages:
        try:
            # Get document
            document = model.Document(database, imapMessage.id)
        # If the document has been deleted,
        except xapian.DocNotFoundError:
            # Skip it
            logging.debug('Unable to load document %s', imapMessage.id)
            continue
        # Get partPacks and attachmentPacks
        partPacks, attachmentPacks = model.getRelatedPacks(pathStore, imapMessage.id)
        # Append
        matches.append(dict(
            document=document, 
            message=imapMessage,
            partPacks=partPacks,
            attachmentPacks=attachmentPacks,
        ))
    # Return
    return matches, lambda x: query_process.TextMachine(highlightTemplate='<span class=highlight>%s</span>', escape=h.html_escape).process(queryString, x.getContent())


class MatchDecider(xapian.MatchDecider):

    def __init__(self, owner_id, messageTagID, attachmentExtensionID):
        xapian.MatchDecider.__init__(self)
        self.owner_id = owner_id
        self.messageTagText = getMessageTagText(messageTagID)
        self.messageTagID = messageTagID
        self.attachmentExtensionText = getAttachmentExtensionText(attachmentExtensionID)
        self.attachmentExtensionID = attachmentExtensionID

    def __call__(self, document):
        # Evaluate privacy
        privacy = xapian.sortable_unserialise(document.get_value(model.xapian_privacy))
        if privacy != 0 and privacy != self.owner_id:
            return False
        # Evaluate messageTag
        if self.messageTagID != 'any':
            messageTagString = document.get_value(model.xapian_messageTags)
            if self.messageTagText not in messageTagString.splitlines():
                return False
        # Evaluate attachmentExtensionText
        if self.attachmentExtensionID != 'can':
            attachmentExtensionString = document.get_value(model.xapian_attachmentExtensions)
            if self.attachmentExtensionID == 'must':
                if not attachmentExtensionString:
                    return False
            elif self.attachmentExtensionText not in attachmentExtensionString.splitlines():
                return False
        # Return
        return True


def adjustStartIndex(startIndex, totalCount=0):
    'Return adjusted start index'
    try:
        startIndex = int(startIndex)
    except ValueError:
        startIndex = 0
    try:
        totalCount = int(totalCount)
    except ValueError:
        totalCount = 0
    startIndex = max(startIndex, 0)
    startIndex = min(startIndex, max(0, totalCount - parameter.RESULTS_PER_PAGE))
    return startIndex


def getMessageTagText(messageTagID):
    # Check for special cases
    if messageTagID == 'any':
        return None
    # Load
    messageTag = meta.Session.query(model.IMAPMessageTag).get(messageTagID)
    # Return
    if messageTag:
        return messageTag.text
    else:
        return None


def getAttachmentExtensionText(attachmentExtensionID):
    # Check for special cases
    if attachmentExtensionID in ['can', 'must']:
        return None
    # Load
    attachmentExtension = meta.Session.query(model.AttachmentExtension).get(attachmentExtensionID)
    # Return
    if attachmentExtension:
        return attachmentExtension.text
    else:
        return None
