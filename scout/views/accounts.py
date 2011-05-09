'Views for IMAP accounts'
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from scout.models import db, User, IMAPAccount


def includeme(config):
    config.scan(__name__)
    config.add_route('account_index', '/accounts')
    config.add_route('account_add', '/accounts/add')
    # map.connect('account_check', '/accounts/{accountID}/check', controller='accounts', action='check')
    # map.connect('account_update', '/accounts/{accountID}/update', controller='accounts', action='update')


@view_config(route_name='account_index', renderer='accounts/index.mak', permission='protected')
def index(request):
    'Show registered IMAP accounts'
    imapAccountQuery = db.query(IMAPAccount).options(joinedload(IMAPAccount.user))
    personQuery = db.query(User.id, User.nickname)
    # statements = [Session.query(model.IMAPMessage.imap_account_id, sa.func.count('*').label('message_count')).filter(model.IMAPMessage.message_status>model.message_incomplete).group_by(model.IMAPMessage.imap_account_id).subquery()]
    # columns = [model.IMAPAccount] + [x.c.message_count for x in statements]
    # imapAccountQuery = Session.query(*columns).options(orm.eagerload(model.IMAPAccount.owner))
    # for statement in statements:
        # imapAccountQuery = imapAccountQuery.outerjoin((statement, model.IMAPAccount.id==statement.c.imap_account_id))
    return dict(imapAccountPacks=imapAccountQuery.all(), personPacks=personQuery.all())


@view_config(route_name='account_add', renderer='json', request_method='POST', permission='protected')
def add(request):
    'Add IMAP account'
    params = request.params
    if params.get('token') != request.session.get_csrf_token():
        return dict(isOk=0, message='Invalid token')
    accountUserID = params.get('accountUserID', 0)
    accountHost = params.get('accountHost', '')
    accountUsername = params.get('accountUsername', '')
    accountPassword = params.get('accountPassword', '')
    # Check user
    if not db.query(User).get(accountUserID):
        return dict(isOk=0, message='Could not find accountUserID=%s' % accountUserID)
    # Check account credentials using validators
    try:
        form = IMAPAccountForm().to_python(params)
    except Invalid, error:
        return dict(isOk=0, errorByID=error.unpack_errors())
    # Check account credentials by login
    imapAccount = IMAPAccount(user_id=accountUserID, host=accountHost, username=accountUsername, password=accountPassword)
    if not checkIMAPAccount(imapAccount):
        return dict(isOk=0, message='Could not log into account')
    # Add
    db.add(imapAccount)
    # Return
    return dict(isOk=1, content=render('accounts/accounts.mak', index(request), request))


class IMAPAccountForm(Schema):
    'IMAP account validator'

    allow_extra_fields = True
    filter_extra_fields = True

    accountUserID = All(
    )
    accountHost = All(
    )
    accountUsername = All(
    )
    accountPassword = All(
    )

    username = All(
        validators.UnicodeString(
            min=USERNAME_LEN_MIN,
            max=USERNAME_LEN_MAX,
            not_empty=True,
            strip=True),
        Unique('username', 'That username already exists'))
    password = All(
        validators.UnicodeString(
            min=PASSWORD_LEN_MIN,
            not_empty=True),
        SecurePassword())
    nickname = All(
        validators.UnicodeString(
            min=NICKNAME_LEN_MIN,
            max=NICKNAME_LEN_MAX,
            not_empty=True,
            strip=True),
        Unique('nickname', 'That nickname already exists'))
    email = All(
        validators.UnicodeString(
            max=EMAIL_LEN_MAX,
            not_empty=True,
            strip=True),
        validators.Email(),
        Unique('email', 'That email is reserved for another account'))


def checkIMAPAccount(imapAccount):
    'Check IMAP account credentials'
    try:
        server = imaplib.IMAP4_SSL(imapAccount.host)
        server.login(imapAccount.username, imapAccount.password)
    except imaplib.IMAP4.error:
        return dict(isOk=0)
    else:
        return dict(isOk=1)
