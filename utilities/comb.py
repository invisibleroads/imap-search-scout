#!/usr/local/bin/python2.6


'Comb internal database using rules'


# Import system modules
from sqlalchemy import orm
import xapian
# Import custom modules
import script_process
from scout import model
from scout.model import meta
from scout.lib import mail_process


def run(forceComb):
    # Initialize
    index = mail_process.Index(pathStore)
    countByType = {
        'visibility_automatic': 0,
        'visibility_hide': 0,
        'visibility_show': 0,
        'visibility_delete': 0,
        'account': 0,
    }
    # For each message with pending changes,
    for message in meta.Session.query(model.IMAPMessage).options(orm.eagerload(model.IMAPMessage.imap_account)).filter_by(message_status_changed=True):
        # Get
        messageStatus = message.message_status
        # If the message's visibility is automatic,
        if messageStatus == model.message_ok:
            countByType['visibility_automatic'] += 1
        else:
            if messageStatus == model.message_hide:
                countByType['visibility_hide'] += 1
            elif messageStatus == model.message_show:
                countByType['visibility_show'] += 1
            elif messageStatus == model.message_delete:
                countByType['visibility_delete'] += 1
        # Update
        index.update(message)
        message.message_status_changed = False
    # Commit
    meta.Session.commit()
    # For each person,
    for person in meta.Session.query(model.Person):
        # Skip combing if the rules have not changed
        if not forceComb and not person.when_modified_rule: 
            continue
        # For each imapAccount,
        for imapAccount in person.imap_accounts:
            # Show feedback
            print 'Combing %s@%s using rules for %s' % (imapAccount.username, imapAccount.host, person.nickname)
            countByType['account'] += 1
            # For each imapMessage,
            for message in meta.Session.query(model.IMAPMessage).filter_by(message_status=model.message_ok).filter_by(imap_account_id=imapAccount.id):
                # Update
                index.update(message)
        # Clear
        person.when_modified_rule = None
    # Commit
    return '%(account)s accounts updated, %(visibility_automatic)s messages set to automatic visibility, %(visibility_hide)s messages forcibly hidden, %(visibility_show)s messages forcibly shown, %(visibility_delete)s messages deleted' % countByType


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    optionParser.add_option('-f', '--forceComb', dest='forceComb', help='force combing even if rules have not changed', action='store_true', default=False)
    options, args = optionParser.parse_args()
    # Initialize
    pathStore = script_process.initialize(options)[1]
    # Run
    try:
        print model.clean(pathStore)
        print run(options.forceComb)
    except xapian.DatabaseLockError:
        pass
    else:
        meta.Session.commit()
