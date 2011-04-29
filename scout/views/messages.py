'Views for IMAP messages'
from pyramid.view import view_config


def includeme(config):
    config.scan(__name__)
    # map.connect('message_index', '/', controller='messages', action='index')
    # map.connect('message_search', '/search', controller='messages', action='search')
    # map.connect('message_update', '/{documentID}/update', controller='messages', action='update')
    # map.connect('message_revive', '/{documentID}/revive', controller='messages', action='revive') 
    # map.connect('message_download', '/{documentID}/download', controller='messages', action='download')
    # map.connect('message_download_file', '/{documentID}/download/{fileIndex}', controller='messages', action='download')
