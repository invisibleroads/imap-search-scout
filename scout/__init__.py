'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from sqlalchemy import engine_from_config
from ConfigParser import ConfigParser
import os

from scout.libraries import tools
from scout.models import initialize_sql
from scout.views import pages, users, accounts
from scout.parameters import *


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Load sensitive configuration
    if '__file__' in global_config:
        configFolder, configName = os.path.split(global_config['__file__'])
        configParser = ConfigParser(global_config)
        if configParser.read(os.path.join(configFolder, '.' + configName)):
            for section in configParser.sections():
                settings.update(configParser.items(section))
    if 'hashlib.secret' in settings:
        tools.secret = settings['hashlib.secret']
    # Connect to database
    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))
    # Define methods
    def get_groups(userID, request):
        'Return a list of groups associated with the authenticated user'
        identity = authenticationPolicy.cookie.identify(request)
        if identity:
            return identity['tokens'][1:]
    def make_renderer_globals(system):
        'Define template constants'
        identity = authenticationPolicy.cookie.identify(system['request'])
        if identity:
            userID = identity['userid']
            nickname, offset, groups = users.parse_tokens(identity['tokens'])
        else:
            userID = None
            nickname, offset, groups = u'', MINUTES_OFFSET, []
        return dict(
            SITE_NAME=SITE_NAME, 
            SITE_VERSION=SITE_VERSION,
            USER_ID=userID,
            USER_NICKNAME=nickname,
            USER_OFFSET=offset,
            USER_GROUPS=groups)
    # Prepare configuration
    if 'authtkt.secret' not in settings:
        settings['authtkt.secret'] = tools.make_random_string(SECRET_LEN)
    authenticationPolicy = AuthTktAuthenticationPolicy(settings['authtkt.secret'], 
        callback=get_groups, http_only=True)
    config = Configurator(
        settings=settings,
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='protected',
        renderer_globals_factory=make_renderer_globals,
        root_factory='scout.RootFactory')
    config.add_settings({
        'mako.directories': 'scout:templates',
        'mako.default_filters': 'h',
        'cache.regions': 'short, medium, long',
    })
    # Configure transaction manager and mailer
    config.include('pyramid_tm')
    config.include('pyramid_mailer')
    # Configure sessions and caching
    if 'session.secret' not in settings:
        settings['session.secret'] = tools.make_random_string(SECRET_LEN)
    config.set_session_factory(session_factory_from_settings(settings))
    set_cache_regions_from_settings(settings)
    # Configure static assets
    config.add_static_view('static', 'scout:static')
    # Configure routes for user account management
    config.include(users)
    # Configure routes that demonstrate access control
    config.include(pages)
    # Configure routes for IMAP accounts
    config.include(accounts)
    # Configure routes for IMAP messages
    # map.connect('message_index', '/', controller='messages', action='index')
    # map.connect('message_search', '/search', controller='messages', action='search')
    # map.connect('message_update', '/{documentID}/update', controller='messages', action='update')
    # map.connect('message_revive', '/{documentID}/revive', controller='messages', action='revive') 
    # map.connect('message_download', '/{documentID}/download', controller='messages', action='download')
    # map.connect('message_download_file', '/{documentID}/download/{fileIndex}', controller='messages', action='download')
    # Configure routes for IMAP rules
    # map.connect('rule_index', '/rules', controller='rules', action='index')
    # map.connect('rule_add', '/rules/add', controller='rules', action='add')
    # map.connect('rule_remove', '/rules/remove', controller='rules', action='remove')
    # Return WSGI app
    return config.make_wsgi_app()


class RootFactory(object):
    'Permission definitions'
    __acl__ = [ 
        (Allow, Authenticated, 'protected'),
        (Allow, 'x', 'privileged'),
    ]

    def __init__(self, request):
        pass
