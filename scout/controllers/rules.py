'Rules controller'
# Import pylons modules
from pylons import request, tmpl_context as c
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
import datetime
# Import custom modules
from scout import model
from scout.model import Session
from scout.lib import helpers as h
from scout.lib.base import BaseController, render
from scout.controllers import requireLogin, requireLoginJSON


class RulesController(BaseController):

    @requireLogin
    def index(self):
        'Show rules for processing email'
        return render('/rules/index.mako')

    @jsonify
    @requireLoginJSON
    def add(self):
        'Add rule'
        # Load
        ruleType = parseRuleType(request.POST.get('action', ''))
        ruleFrom = request.POST.get('from', '').strip()
        ruleTo = request.POST.get('to', '').strip()
        ruleSubject = request.POST.get('subject', '').strip()
        # If the rule is invalid or empty, ignore it
        if ruleType == None or ruleFrom + ruleTo + ruleSubject == '':
            return dict(isOk=0, message='Rule is invalid or empty')
        # Get
        personID = h.getPersonID()
        person = Session.query(model.Person).get(personID)
        if not person:
            return dict(isOk=0, message='Could not find personID=%s' % personID)
        # Add
        Session.add(model.IMAPMessageRule(personID, ruleType, ruleFrom, ruleTo, ruleSubject))
        person.when_modified_rule = datetime.datetime.utcnow()
        # Commit
        Session.commit()
        # Return
        return dict(isOk=1, content=render('/rules/rules.mako'))

    @jsonify
    @requireLoginJSON
    def remove(self):
        'Remove rule'
        # Initialize
        personID = h.getPersonID()
        person = Session.query(model.Person).get(personID)
        if not person:
            return dict(isOk=0, message='Could not find personID=%s' % personID)
        # Remove
        Session.execute(model.imap_message_rules_table.delete().where((model.IMAPMessageRule.id==request.POST.get('ruleID', 0)) & (model.IMAPMessageRule.owner_id==personID)))
        # Update
        person.when_modified_rule = datetime.datetime.utcnow()
        # Commit
        Session.commit()
        # Return
        return dict(isOk=1)


# Helpers

def parseRuleType(action):
    'Determine the rule type number from the action text'
    try:
        return {
            'hide': model.action_hide,
        }[action]
    except KeyError:
        return None
