# Import pylons modules
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
import imaplib
from sqlalchemy import orm
# Import custom modules
from scout.lib.base import BaseController, render
from scout.lib import helpers as h
from scout.model import meta
from scout import model


class AccountController(BaseController):

    withAuthentication = True

    def index(self):
        c.imapAccounts = meta.Session.query(model.IMAPAccount).options(orm.eagerload(model.IMAPAccount.owner))
        c.people = meta.Session.query(model.Person).order_by(model.Person.is_active.desc(), model.Person.id)
        return render('/emails/accounts.mako')

    def activate(self):
        # Load
        imapAccountID = int(request.POST['id'])
        imapAccount = meta.Session.query(model.IMAPAccount).get(imapAccountID)
        # Check credentials
        if h.isPersonSuper() or session['personID'] == imapAccount.owner_id:
            # Load
            is_active = bool(int(request.POST['is_active']))
            # If it exists,
            if imapAccount:
                # Deactivate
                imapAccount.is_active = is_active
                # Commit
                meta.Session.commit()

    @jsonify
    def check(self):
        # Load
        imapAccountID = int(request.GET['id'])
        imapAccount = meta.Session.query(model.IMAPAccount).get(imapAccountID)
        # If it exists,
        if imapAccount:
            # Return
            return checkIMAPAccount(imapAccount)

    @jsonify
    def change(self):
        # Load
        imapAccountID = int(request.POST['id'])
        imapAccount = meta.Session.query(model.IMAPAccount).get(imapAccountID)
        # Check credentials
        if h.isPersonSuper() or session['personID'] == imapAccount.owner_id:
            # Change
            imapAccount.password = request.POST['password'] 
            meta.Session.commit()
            # Return
            return checkIMAPAccount(imapAccount)
                    
    @jsonify
    def add(self):
        # Initialize
        if h.isPersonSuper():
            # Load
            accountOwnerID = int(request.POST['ownerID'])
            accountHost = request.POST['host']
            accountUsername = request.POST['username']
            accountPassword = request.POST['password']
            # Make sure the owner exists
            if not meta.Session.query(model.Person).get(accountOwnerID):
                return {'isOk': 0}
            # Set
            imapAccount = model.IMAPAccount(accountOwnerID, accountHost, accountUsername, accountPassword)
            # Check
            result = checkIMAPAccount(imapAccount)
            if result['isOk']:
                meta.Session.add(imapAccount)
                meta.Session.commit()
            # Return
            return result


def checkIMAPAccount(imapAccount):
    # Try to connect
    try:
        server = imaplib.IMAP4(imapAccount.host)
        server.login(imapAccount.username, imapAccount.password)
    except imaplib.IMAP4.error:
        return {'isOk': 0}
    else:
        return {'isOk': 1}
