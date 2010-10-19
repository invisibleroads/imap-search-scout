#!/usr/local/bin/python2.6


"""
[nickname]
username = STRING
password = STRING
email = STRING
super = BOOLEAN
active = BOOLEAN
accounts = 
    HOST USERNAME PASSWORD
rules = 
    hide from(STRING) to(STRING) subject(STRING) tag(STRING)
"""


# Import system modules
import ConfigParser
import re
# Import custom modules
import script_process
from scout import model
from scout.model import meta


# Set patterns

pattern_from = re.compile(r'from\(([^)]*)\)', re.I)
pattern_to = re.compile(r'to\(([^)]*)\)', re.I)
pattern_subject = re.compile(r'subject\(([^)]*)\)', re.I)
pattern_tag = re.compile(r'tag\(([^)]*)\)', re.I)


# Core

def run(peoplePath):
    'Initialize accounts'
    # Initialize
    newPersonCount = 0
    newAccountCount = 0
    newRuleCount = 0
    # Load peoplePath
    configParser = ConfigParser.ConfigParser()
    configParser.read(peoplePath)
    # Load people
    people = []
    for nickname in configParser.sections():
        # Define
        getValue = lambda valueName: configParser.get(nickname, valueName).strip()
        # Parse accounts
        imapAccounts = []
        for line in getValue('accounts').splitlines():
            # Split
            imapHost, imapUsername, imapPassword = line.split()
            # Append
            imapAccounts.append({
                'host': imapHost, 
                'username': imapUsername, 
                'password': imapPassword
            })
        # Parse rules
        rules = []
        def getPattern(pattern):
            match = pattern.search(line)
            return match.group(1).strip() if match else ''
        for lineIndex, line in enumerate(getValue('rules').splitlines()):
            # Split
            action = line.split()[0]
            ruleType = {
                'hide': model.action_hide,
            }[action]
            # Append
            rules.append({
                'type': ruleType,
                'from': unicode(getPattern(pattern_from)),
                'to': unicode(getPattern(pattern_to)),
                'subject': unicode(getPattern(pattern_subject)),
                'tag': unicode(getPattern(pattern_tag)),
                'priority': lineIndex + 1,
            })
        # Append
        people.append({
            'username': getValue('username'),
            'password': getValue('password'),
            'nickname': unicode(nickname),
            'email': getValue('email'),
            'email_sms': getValue('email_sms'),
            'is_super': getValue('super'),
            'is_active': getValue('active'),
            'accounts': imapAccounts,
            'rules': rules,
        })
    # Add people
    for personPack in people:
        # Add person
        person = meta.Session.query(model.Person).filter_by(username=personPack['username']).first()
        if not person:
            print 'Adding person\t\t%s' % personPack['nickname']
            person = model.Person(
                personPack['username'], 
                model.hashString(personPack['password']), 
                personPack['nickname'], 
                personPack['email'], 
                personPack['email_sms'], 
                personPack['is_super'], 
                personPack['is_active']
            )
            meta.Session.add(person)
            meta.Session.commit()
            newPersonCount += 1
        # Add imapAccounts
        for accountPack in personPack['accounts']:
            if not meta.Session.query(model.IMAPAccount).filter_by(username=accountPack['username']).first():
                print 'Adding imap account\t%s@%s' % (accountPack['username'], accountPack['host'])
                imapAccount = model.IMAPAccount(
                    person.id, 
                    accountPack['host'],
                    accountPack['username'],
                    accountPack['password'],
                )
                meta.Session.add(imapAccount)
                newAccountCount += 1
        # Remember
        personPack['person'] = person
    # Add rules
    personByNickname = dict((x['nickname'].lower(), x['person']) for x in people)
    for personPack in people:
        person = personPack['person']
        for rulePack in personPack['rules']:
            if not meta.Session.query(model.IMAPMessageRule).filter_by(owner_id=person.id, type=rulePack['type'], from_whom=rulePack['from'], to_whom=rulePack['to'], subject=rulePack['subject'], tag=rulePack['tag']).first():
                rule = model.IMAPMessageRule(
                    person.id, 
                    rulePack['type'], 
                    rulePack['from'], 
                    rulePack['to'], 
                    rulePack['subject'], 
                    rulePack['tag'], 
                    rulePack['priority']
                )
                print 'Adding rule\t\t%s %s' % (person.nickname, rule)
                meta.Session.add(rule)
                newRuleCount += 1
    # Return
    return 'Added %s people, %s accounts, %s rules' % (newPersonCount, newAccountCount, newRuleCount)


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    optionParser.add_option('-p', '--peoplePath', dest='peoplePath', help='use the specified people configuration file', metavar='PATH', default=script_process.expandBasePath('people.cfg'))
    options, args = optionParser.parse_args()
    # Initialize
    pathStore = script_process.initialize(options)[1]
    # Run
    print run(options.peoplePath)
    meta.Session.commit()
