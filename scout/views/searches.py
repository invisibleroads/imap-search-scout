'Views for IMAP searches'
from pyramid.view import view_config


def includeme(config):
    config.scan(__name__)
    # map.connect('rule_index', '/rules', controller='rules', action='index')
    # map.connect('rule_add', '/rules/add', controller='rules', action='add')
    # map.connect('rule_remove', '/rules/remove', controller='rules', action='remove')
