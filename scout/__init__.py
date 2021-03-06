'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from sqlalchemy import engine_from_config
from sqlalchemy.pool import QueuePool, NullPool
from ConfigParser import ConfigParser
import os

from scout.libraries import tools
from scout.models import initialize_sql
from scout.views import pages, users, accounts, messages, searches
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
        tools.secret1 = settings['hashlib.secret']
    if 'ciphers.secret' in settings:
        tools.secret2 = settings['ciphers.secret']
    # Connect to database
    sqlalchemyURL = settings['sqlalchemy.url'].strip()
    initialize_sql(engine_from_config(settings, 'sqlalchemy.', 
        poolclass=NullPool if sqlalchemyURL.startswith('sqlite:///') else QueuePool))
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
            IS_SUPER='s' in groups)
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
    config.include(messages)
    # Configure routes for IMAP searches
    config.include(searches)
    # Return WSGI app
    return config.make_wsgi_app()


class RootFactory(object):
    'Permission definitions'
    __acl__ = [ 
        (Allow, Authenticated, 'protected'),
        (Allow, 's', 'privileged'),
    ]

    def __init__(self, request):
        pass
