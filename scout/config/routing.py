'URL configuration'
# Import pylons modules
from routes import Mapper


def make_map(config):
    'Create, configure and return the routes mapper'
    # Initialize map
    map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    map.minimization = False
    map.explicit = False
    # Remove trailing slash
    map.redirect('/{controller}/', '/{controller}')
    # Map errors
    map.connect('/errors/{action}', controller='errors')
    map.connect('/errors/{action}/{id}', controller='errors')
    # Map people
    map.connect('person_index', '/people', controller='people', action='index')
    map.connect('person_register', '/people/register', controller='people', action='register', conditions=GET)
    map.connect('person_register', '/people/register', controller='people', action='register_', conditions=POST)
    map.connect('person_confirm', '/people/confirm/{ticket}', controller='people', action='confirm')
    map.connect('person_login', '/people/login', controller='people', action='login', conditions=GET)
    map.connect('person_login', '/people/login', controller='people', action='login_', conditions=POST)
    map.connect('person_update', '/people/update', controller='people', action='update', conditions=GET)
    map.connect('person_update', '/people/update', controller='people', action='update_', conditions=POST)
    map.connect('person_logout', '/people/logout', controller='people', action='logout')
    map.connect('person_reset', '/people/reset', controller='people', action='reset')
    # Map accounts
    map.connect('account_index', '/accounts', controller='accounts', action='index')
    map.connect('account_add', '/accounts/add', controller='accounts', action='add')
    map.connect('account_check', '/accounts/{accountID}/check', controller='accounts', action='check')
    map.connect('account_update', '/accounts/{accountID}/update', controller='accounts', action='update')
    # Map messages
    map.connect('message_index', '/', controller='messages', action='index')
    map.connect('message_search', '/search', controller='messages', action='search')
    map.connect('message_update', '/{documentID}/update', controller='messages', action='update')
    map.connect('message_revive', '/{documentID}/revive', controller='messages', action='revive') 
    map.connect('message_download', '/{documentID}/download', controller='messages', action='download')
    map.connect('message_download_file', '/{documentID}/download/{fileIndex}', controller='messages', action='download')
    # Map rules
    map.connect('rule_index', '/rules', controller='rules', action='index')
    map.connect('rule_add', '/rules/add', controller='rules', action='add')
    map.connect('rule_remove', '/rules/remove', controller='rules', action='remove')
    # Return
    return map
