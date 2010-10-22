'Accounts controller'
# Import pylons modules
from pylons import request, session, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.decorators import jsonify
# Import system modules
import imaplib
import sqlalchemy as sa
from sqlalchemy import orm
# Import custom modules
from scout import model
from scout.model import Session
from scout.lib import helpers as h
from scout.lib.base import BaseController, render


class AccountsController(BaseController):
    'Methods to handle account add, update, check'

    def index(self):
        'Show registered IMAP accounts'
        # If the user is not logged in,
        if not h.isPerson():
            return redirect(url('person_login', targetURL=h.encodeURL(request.path)))
        # Prepare
        statements = [Session.query(model.IMAPMessage.imap_account_id, sa.func.count('*').label('message_count')).filter(model.IMAPMessage.message_status>model.message_incomplete).group_by(model.IMAPMessage.imap_account_id).subquery()]
        columns = [model.IMAPAccount] + [x.c.message_count for x in statements]
        imapAccountQuery = Session.query(*columns).options(orm.eagerload(model.IMAPAccount.owner))
        for statement in statements:
            imapAccountQuery = imapAccountQuery.outerjoin((statement, model.IMAPAccount.id==statement.c.imap_account_id))
        # Load
        c.imapAccounts = imapAccountQuery.all()
        c.people = Session.query(model.Person).order_by(model.Person.is_active.desc(), model.Person.id)
        # Return
        return render('/accounts/index.mako')

    @jsonify
    def add(self):
        'Add IMAP account'
        # If the user is not logged in,
        if not h.isPersonSuper():
            return dict(isOk=0, message='Access denied')
        # Load
        ownerID = int(request.POST.get('ownerID', 0))
        host = request.POST.get('host', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # Make sure the owner exists
        if not Session.query(model.Person).get(ownerID):
            return dict(isOk=0, message='Could not find ownerID=%s' % ownerID)
        # Set
        imapAccount = model.IMAPAccount(ownerID, host, username, password)
        # Check
        result = checkIMAPAccount(imapAccount)
        if result['isOk']:
            Session.add(imapAccount)
            Session.commit()
        # Return
        return result

    @jsonify
    def check(self, accountID):
        'Check credentials'
        # If the user is not logged in,
        if not h.isPerson():
            return dict(isOk=0, message='Access denied')
        # Load
        try:
            imapAccount = loadIMAPAccount(accountID)
        except IMAPAccountError, error:
            return dict(isOk=0, message=str(error))
        # Return
        return checkIMAPAccount(imapAccount)

    @jsonify
    def update(self, accountID):
        'Update account credentials'
        # If the user is not logged in,
        if not h.isPerson():
            return dict(isOk=0, message='Access denied')
        # Load
        try:
            imapAccount = loadIMAPAccount(accountID)
        except IMAPAccountError, error:
            return dict(isOk=0, message=str(error))
        personID = h.getPersonID()
        # Check credentials
        if not (h.isPersonSuper() or personID == imapAccount.owner_id):
            return dict(isOk=0, message='Access denied')
        # If the user wants to change the password,
        if 'password' in request.POST:
            imapAccount.password = request.POST['password'] 
            Session.commit()
            return checkIMAPAccount(imapAccount)
        # If the user wants to activate or deactivate the account,
        if 'is_active' in request.POST:
            try:
                is_active = bool(int(request.POST['is_active']))
            except ValueError:
                return dict(isOk=0, message='The is_active flag must be either 0 or 1')
            imapAccount.is_active = is_active
            Session.commit()
            return dict(isOk=1)


# Helpers

def loadIMAPAccount(accountID):
    'Load account'
    # Load accountID
    try:
        accountID = int(accountID)
    except ValueError:
        raise IMAPAccountError('The accountID must be an integer')
    # Load imapAccount
    imapAccount = Session.query(model.IMAPAccount).get(accountID)
    if not imapAccount:
        raise IMAPAccountError('Could not find accountID=%s' % accountID)
    # Return
    return imapAccount

def checkIMAPAccount(imapAccount):
    'Check credentials'
    try:
        server = imaplib.IMAP4(imapAccount.host)
        server.login(imapAccount.username, imapAccount.password)
    except imaplib.IMAP4.error:
        return dict(isOk=0)
    else:
        return dict(isOk=1)

class IMAPAccountError(Exception):
    pass
