'Database objects'
# Import system modules
import sqlalchemy as sa
import sqlalchemy.orm as orm
import hashlib
import warnings; warnings.simplefilter('error')
import datetime
import xapian
import shutil
import glob
import os; basePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging; logging.basicConfig(filename=os.path.join(basePath, 'logs/mail.log'), level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
# Import custom modules
from scout.model.meta import Session, Base
from scout.config import parameter
# Set constants
xapian_date, xapian_privacy, xapian_messageTags, xapian_attachmentExtensions = xrange(4)
action_hide = 0
message_incomplete, message_ok, message_hide, message_show, message_delete = xrange(5)


# Define methods

def init_model(engine):
    'Call me before using any of the tables or classes in the model'
    Session.configure(bind=engine)

def hashString(string): 
    'Compute the hash of the string'
    return hashlib.sha256(string).digest()


# Define tables

people_table = sa.Table('people', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('password_hash', sa.LargeBinary(32), nullable=False),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('email_sms', sa.String(parameter.EMAIL_LENGTH_MAXIMUM)),
    sa.Column('minutes_offset', sa.Integer, default=0),
    sa.Column('rejection_count', sa.Integer, default=0),
    sa.Column('is_super', sa.Boolean, default=False),
    sa.Column('is_active', sa.Boolean, default=True),
    sa.Column('when_modified_rule', sa.DateTime),
)
person_candidates_table = sa.Table('person_candidates', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM), nullable=False),
    sa.Column('password_hash', sa.LargeBinary(32), nullable=False),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM), nullable=False),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), nullable=False),
    sa.Column('email_sms', sa.String(parameter.EMAIL_LENGTH_MAXIMUM)),
    sa.Column('ticket', sa.String(parameter.TICKET_LENGTH), unique=True, nullable=False),
    sa.Column('when_expired', sa.DateTime, nullable=False),
    sa.Column('person_id', sa.ForeignKey('people.id')),
)
imap_accounts_table = sa.Table('imap_accounts', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('host', sa.String(parameter.HOST_LENGTH_MAXIMUM)),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM)),
    sa.Column('password', sa.String(parameter.PASSWORD_LENGTH_MAXIMUM)),
    sa.Column('is_active', sa.Boolean(), default=True),
    sa.Column('when_archived', sa.DateTime),
    sa.UniqueConstraint('host', 'username')
)
imap_messages_table = sa.Table('imap_messages', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('imap_account_id', sa.ForeignKey('imap_accounts.id')),
    sa.Column('when', sa.DateTime),
    sa.Column('from_whom', sa.Unicode(parameter.WHOM_LENGTH_MAXIMUM)),
    sa.Column('to_cc_bcc', sa.UnicodeText),
    sa.Column('subject', sa.Unicode(parameter.SUBJECT_LENGTH_MAXIMUM)),
    sa.Column('message_hash', sa.Binary(32)),
    sa.Column('message_status', sa.Integer, default=message_incomplete),
    sa.Column('message_status_changed', sa.Boolean, default=False),
    sa.Column('privacy', sa.Integer, default=0),
)
imap_message_rules_table = sa.Table('imap_message_rules', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('type', sa.Integer),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('from_whom', sa.Unicode(parameter.WHOM_LENGTH_MAXIMUM)),
    sa.Column('to_whom', sa.Unicode(parameter.WHOM_LENGTH_MAXIMUM)),
    sa.Column('subject', sa.Unicode(parameter.SUBJECT_LENGTH_MAXIMUM)),
    sa.Column('tag', sa.Unicode(parameter.TAG_LENGTH_MAXIMUM)),
    sa.Column('priority', sa.Integer, default=1),
)
imap_message_tags_table = sa.Table('imap_message_tags', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('text', sa.Unicode(parameter.TAG_LENGTH_MAXIMUM)),
)
imap_message_tag_links_table = sa.Table('imap_message_tag_links', Base.metadata,
    sa.Column('imap_message_id', sa.ForeignKey('imap_messages.id'), primary_key=True),
    sa.Column('tag_id', sa.ForeignKey('imap_message_tags.id'), primary_key=True),
)
attachment_extensions_table = sa.Table('attachment_extensions', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('text', sa.Unicode(parameter.ATTACHMENT_EXTENSION_LENGTH_MAXIMUM)),
)
imap_message_attachment_extension_links_table = sa.Table('imap_message_attachment_extension_links', Base.metadata,
    sa.Column('imap_message_id', sa.ForeignKey('imap_messages.id'), primary_key=True),
    sa.Column('attachment_extension_id', sa.ForeignKey('attachment_extensions.id'), primary_key=True),
)


# Define classes

class Person(object):

    def __init__(self, username, password_hash, nickname, email, email_sms=''):
        self.username = username
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.email_sms = email_sms

    def __repr__(self):
        return "<Person('%s')>" % self.username


class PersonCandidate(Person):

    def __repr__(self):
        return "<PersonCandidate('%s')>" % self.username


class IMAPAccount(object):

    def __init__(self, owner_id, host, username, password):
        self.owner_id = owner_id
        self.host = host
        self.username = username
        self.password = password

    def __repr__(self):
        return "<IMAPAccount('%s@%s')>" % (self.username, self.host)


class IMAPMessage(object):

    def __init__(self, imap_account, subject, from_whom, to_cc_bcc, when):
        self.imap_account = imap_account
        self.subject = subject[:parameter.SUBJECT_LENGTH_MAXIMUM]
        self.from_whom = from_whom[:parameter.WHOM_LENGTH_MAXIMUM]
        self.to_cc_bcc = to_cc_bcc
        self.when = when
        self.message_hash = hashString(subject)

    def __repr__(self):
        return "<IMAPMessage('%s')>" % (self.subject)

    def setTags(self, tagTexts):
        # Convert tagTexts
        tagTexts = [unicode(x) for x in sorted(tagTexts)]
        # If nothing has changed, return
        if tagTexts == sorted([x.text for x in self.tags]):
            return
        # Get
        oldTags = Base.Session.query(IMAPMessageTag).filter(IMAPMessageTag.text.in_(tagTexts)).all()
        newTags = [IMAPMessageTag(tagText[:parameter.TAG_LENGTH_MAXIMUM]) for tagText in set(tagTexts).difference(oldTag.text for oldTag in oldTags)]
        # Add
        if newTags:
            for newTag in newTags:
                Base.Session.add(newTag)
            Base.Session.commit()
        # Order
        self.tags = oldTags + newTags

    def determinePrivacy(self):
        # Prepare
        tagString = ' '.join(x.text for x in self.tags).lower()
        ownerID = self.imap_account.owner_id
        # If the message visibility is automatic,
        if self.message_status <= message_ok:
            # If we have no flags, load them
            flagByType = decideFlagsFromRules(getRules(ownerID), self)
            # Hide if tags contain keyword "private" or flags indicate privacy
            privacy = ownerID if 'private' in tagString or flagByType[action_hide] else 0
        # If the message visibility is manual,
        else:
            privacy = ownerID if self.message_status == message_hide else 0
        # Return
        return privacy


class IMAPMessageRule(object):

    def __init__(self, owner_id, rule_type, from_whom, to_whom, subject, tag, priority):
        self.owner_id = owner_id
        self.type = rule_type
        self.from_whom = from_whom
        self.to_whom = to_whom
        self.subject = subject
        self.tag = tag
        self.priority = priority

    def __repr__(self):
        terms = ['priority=%s' % self.priority]
        terms.append({
            action_hide: 'hide',
        }[self.type])
        if self.from_whom:
            terms.append('from(%s)' % self.from_whom)
        if self.to_whom:
            terms.append('to(%s)' % self.to_whom)
        if self.subject:
            terms.append('subject(%s)' % self.subject)
        if self.tag:
            terms.append('tag(%s)' % self.tag)
        return ' '.join(terms)


class IMAPMessageTag(object):

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<IMAPMessageTag(%s)>" % (self.text)


class AttachmentExtension(object):

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<AttachmentExtension(%s)>" % (self.text)


class CaseInsensitiveComparator(orm.properties.ColumnProperty.Comparator):

    def __eq__(self, other):
        return sa.func.lower(self.__clause_element__()) == sa.func.lower(other)


# Map classes to tables

orm.mapper(Person, people_table, properties={
    'username': orm.column_property(people_table.c.username, comparator_factory=CaseInsensitiveComparator),
    'nickname': orm.column_property(people_table.c.nickname, comparator_factory=CaseInsensitiveComparator),
    'email': orm.column_property(people_table.c.email, comparator_factory=CaseInsensitiveComparator),
    'email_sms': orm.column_property(people_table.c.email_sms, comparator_factory=CaseInsensitiveComparator),
    'imap_accounts': orm.relation(IMAPAccount, backref='owner'),
})
orm.mapper(PersonCandidate, person_candidates_table)
orm.mapper(IMAPAccount, imap_accounts_table, properties={
    'messages': orm.relation(IMAPMessage, backref='imap_account'),
})
orm.mapper(IMAPMessage, imap_messages_table, properties={
    'tags': orm.relation(IMAPMessageTag, secondary=imap_message_tag_links_table, backref='messages', lazy=False),
    'attachmentExtensions': orm.relation(AttachmentExtension, secondary=imap_message_attachment_extension_links_table, backref='messages', lazy=False),
})
orm.mapper(IMAPMessageTag, imap_message_tags_table)
orm.mapper(IMAPMessageRule, imap_message_rules_table, properties={
    'owner': orm.relation(Person, backref='rules', primaryjoin=imap_message_rules_table.c.owner_id==people_table.c.id),
})
orm.mapper(AttachmentExtension, attachment_extensions_table)


# Helpers

def queryActivePeople():
    return Base.Session.query(Person).filter_by(is_active=True)

def getOldMessage(rawSubject, rawWhen):
    'Try to retrieve the message'
    return Base.Session.query(IMAPMessage).filter_by(when=rawWhen).filter_by(message_hash=hashString(rawSubject)).first()

def getRules(personID):
    return Base.Session.query(IMAPMessageRule).filter_by(owner_id=personID).order_by(IMAPMessageRule.priority.desc(), IMAPMessageRule.id.desc()).all()


# Document wrapper

class Document(object):

    # Constructor

    def __init__(self, database, documentID):
        self.database = database
        self.documentID = documentID
        self.document = database.get_document(documentID)
        self.hasChanged = False

    # Core

    def getContent(self):
        return self.document.get_data()

    def getAttribute(self, attributeIndex, asNumber=False):
        value = self.document.get_value(attributeIndex)
        if asNumber:
            return xapian.sortable_unserialise(value)
        else:
            return value

    def setAttribute(self, attributeIndex, newValue, asNumber=False):
        if asNumber:
            newValue = xapian.sortable_serialise(newValue)
        # Compare as strings
        if self.getAttribute(attributeIndex) == newValue:
            return False
        self.document.add_value(attributeIndex, newValue)
        self.hasChanged = True
        return True

    # Derivatives

    def getPrivacy(self):
        return self.getAttribute(xapian_privacy, asNumber=True)

    def setPrivacy(self, newValue):
        return self.setAttribute(xapian_privacy, newValue, asNumber=True)

    def getTags(self):
        return self.getAttribute(xapian_messageTags).splitlines()

    def setTags(self, tagTexts):
        return self.setAttribute(xapian_messageTags, '\n'.join(tagTexts))

    # Flush

    def save(self):
        if self.hasChanged:
            self.database.replace_document(self.documentID, self.document)
            self.hasChanged = False


def clean(pathStore, isThorough=False):
    # Connect
    xapianDatabase = xapian.WritableDatabase(pathStore.getIndexBasePath(), xapian.DB_CREATE_OR_OPEN)
    crapCount = 0
    # Define
    def deleteLocally(imapMessage):
        deleteDocument(xapianDatabase, pathStore, imapMessage)
    # For each incomplete message,
    for imapMessage in Base.Session.query(IMAPMessage).filter_by(message_status=message_incomplete):
        deleteLocally(imapMessage); crapCount += 1
    # If we are checking thorougly,
    if isThorough:
        # For each message,
        for imapMessage in Base.Session.query(IMAPMessage):
            # Try to retrive the message from xapian
            try:
                xapianDatabase.get_document(imapMessage.id)
            except xapian.DocNotFoundError:
                deleteLocally(imapMessage); crapCount += 1
            else:
                # If the document doesn't exist on the hard drive,
                if not os.path.exists(pathStore.fillDocumentPath(imapMessage.id)):
                    deleteLocally(imapMessage); crapCount += 1
    # Commit
    Base.Session.commit()
    if crapCount:
        message = 'Cleaned %s incomplete message(s)' % crapCount
        logging.debug(message)
        return message
    else:
        return 'The database is clean.'


def deleteDocument(xapianDatabase, pathStore, imapMessage):
    # Remove from xapian
    try:
        xapianDatabase.delete_document(imapMessage.id)
    except xapian.DocNotFoundError:
        pass
    # Remove from storage
    try:
        shutil.rmtree(pathStore.fillDocumentPath(imapMessage.id))
    except OSError:
        pass
    # Remove from database
    Base.Session.delete(imapMessage)


def getRelatedPaths(pathStore, documentID):
    return sorted(glob.glob(os.path.join(pathStore.fillDocumentPath(documentID), '*')))


def getRelatedPacks(pathStore, documentID):
    # Initialize
    partPacks, attachmentPacks = [], []
    # For each file,
    for fileNumber, filePath in enumerate(getRelatedPaths(pathStore, documentID)):
        # Extract name
        fileName = os.path.basename(filePath)
        # Ignore common files
        if fileName in ['header.txt', 'tags.txt']: 
            continue
        # Extract extension
        fileBase, fileExtension = os.path.splitext(fileName)
        fileExtension = unicode(fileExtension[1:1 + parameter.ATTACHMENT_EXTENSION_LENGTH_MAXIMUM].lower())
        # If we have a part,
        if fileExtension in ['txt', 'html']:
            partPacks.append((fileNumber, fileName, fileExtension))
        # If we have an attachment,
        else:
            attachmentPacks.append((fileNumber, fileName, fileExtension))
    # Return
    return partPacks, attachmentPacks


def decideFlagsFromRules(rules, imapMessage):
    # Set defaults
    flagByType = {
        action_hide: False, # Don't hide
    }
    # For each rule,
    for rule in rules:
        # Run the gauntlet
        if (rule.from_whom and rule.from_whom.lower() not in imapMessage.from_whom.lower())\
        or (rule.to_whom and rule.to_whom.lower() not in imapMessage.to_cc_bcc.lower())\
        or (rule.subject and rule.subject.lower() not in imapMessage.subject.lower())\
        or (rule.tag and rule.tag.lower() not in ' '.join(x.text for x in imapMessage.tags).lower()): 
            continue
        # Set flag
        if rule.type == action_hide:
            flagByType[action_hide] = True
    # Return
    return flagByType
