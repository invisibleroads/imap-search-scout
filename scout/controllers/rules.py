# Import pylons modules
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
import datetime
# Import custom modules
from scout.lib.base import BaseController, render
from scout.model import meta
from scout import model


class RuleController(BaseController):

    withAuthentication = True

    def index(self):
        return render('/emails/rules.mako')

    def add(self):
        # Initialize
        personID = session['personID']
        # Load
        ruleAction = request.POST['action']
        ruleFrom = request.POST['from'].strip()
        ruleTo = request.POST['to'].strip()
        ruleSubject = request.POST['subject'].strip()
        ruleTag = request.POST['tag'].strip()
        rulePriority = 1
        # Parse
        try:
            ruleType = {
                'hide': model.action_hide,
            }[ruleAction]
        except KeyError:
            pass
        else:
            # Add
            rule = model.IMAPMessageRule(personID, ruleType, ruleFrom, ruleTo, ruleSubject, ruleTag, rulePriority)
            meta.Session.add(rule)
            # Update
            person = meta.Session.query(model.Person).get(personID)
            person.when_modified_rule = datetime.datetime.utcnow()
            meta.Session.commit()
        # Return
        return render('/emails/rules_.mako')

    @jsonify
    def remove(self):
        # Initialize
        ruleID = request.POST['id']
        personID = session['personID']
        # Remove
        meta.Session.execute(model.imap_message_rules_table.delete().where(model.IMAPMessageRule.owner_id==personID).where(model.IMAPMessageRule.id==ruleID))
        # Update
        person = meta.Session.query(model.Person).get(personID)
        person.when_modified_rule = datetime.datetime.utcnow()
        # Commit
        meta.Session.commit()
        # Return
        return {'isOk': 1}
