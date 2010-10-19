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
    map.connect('person_register', '/people/register', controller='people', action='register')
    map.connect('person_register_', '/people/register_', controller='people', action='register_')
    map.connect('person_confirm', '/people/confirm/{ticket}', controller='people', action='confirm')
    map.connect('person_login', '/people/login/{targetURL}', controller='people', action='login')
    map.connect('person_login_plain', '/people/login', controller='people', action='login')
    map.connect('person_login_', '/people/login_', controller='people', action='login_')
    map.connect('person_update', '/people/update', controller='people', action='update')
    map.connect('person_update_', '/people/update_', controller='people', action='update_')
    map.connect('person_logout_plain', '/people/logout', controller='people', action='logout') 
    map.connect('person_logout', '/people/logout/{targetURL}', controller='people', action='logout')
    map.connect('person_reset', '/people/reset', controller='people', action='reset')
    # Map mail pages
    map.connect('mail_index', '/', controller='mail', action='index')
    map.connect('mail_search', '/search', controller='mail', action='search')
    map.connect('mail_download', '/download/{documentID}/{fileNumber}', controller='mail', action='download')
    map.connect('mail_get_plain', '/get', controller='mail', action='get')
    map.connect('mail_get', '/get/{documentID}', controller='mail', action='get')
    map.connect('mail_revive_plain', '/revive', controller='mail', action='revive') 
    map.connect('mail_revive', '/revive/{documentID}', controller='mail', action='revive') 
    map.connect('mail_change_plain', '/change', controller='mail', action='change')
    map.connect('mail_change', '/change/{documentID}', controller='mail', action='change')
    # Map rule pages
    map.connect('rule_index', '/rules', controller='rule', action='index')
    map.connect('rule_add', '/rules/add', controller='rule', action='add')
    map.connect('rule_remove', '/rules/remove', controller='rule', action='remove')
    # Map account pages
    map.connect('account_index', '/accounts', controller='account', action='index')
    map.connect('account_add', '/accounts/add', controller='account', action='add')
    map.connect('account_check', '/accounts/check', controller='account', action='check')
    map.connect('account_change', '/accounts/change', controller='account', action='change')
    map.connect('account_activate', '/accounts/activate', controller='account', action='activate')
    # Return
    return map
