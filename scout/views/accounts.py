'Views for IMAP accounts'
from pyramid.view import view_config


def includeme(config):
    config.scan(__name__)
    config.add_route('account_index', '/accounts')
    # map.connect('account_index', '/accounts', controller='accounts', action='index')
    # map.connect('account_add', '/accounts/add', controller='accounts', action='add')
    # map.connect('account_check', '/accounts/{accountID}/check', controller='accounts', action='check')
    # map.connect('account_update', '/accounts/{accountID}/update', controller='accounts', action='update')


@view_config(route_name='account_index', renderer='accounts/index.mak', permission='protected')
def index(request):
    'Show registered IMAP accounts'
    # statements = [Session.query(model.IMAPMessage.imap_account_id, sa.func.count('*').label('message_count')).filter(model.IMAPMessage.message_status>model.message_incomplete).group_by(model.IMAPMessage.imap_account_id).subquery()]
    # columns = [model.IMAPAccount] + [x.c.message_count for x in statements]
    # imapAccountQuery = Session.query(*columns).options(orm.eagerload(model.IMAPAccount.owner))
    # for statement in statements:
        # imapAccountQuery = imapAccountQuery.outerjoin((statement, model.IMAPAccount.id==statement.c.imap_account_id))
    # c.imapAccounts = imapAccountQuery.all()
    # c.people = Session.query(model.Person).order_by(model.Person.is_active.desc(), model.Person.id)
    return dict()
