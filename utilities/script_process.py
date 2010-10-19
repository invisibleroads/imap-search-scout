'Define common functions for the command-line utilities'


# Import context modules
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
expandBasePath = lambda x: os.path.join(basePath, x)
import sys; sys.path.append(basePath)
# Import system modules
import ConfigParser
import sqlalchemy as sa
import optparse
# Import custom modules
from scout import model
from scout.lib import file_store


def buildOptionParser():
    optionParser = optparse.OptionParser()
    optionParser.add_option('-c', '--configurationPath', dest='configurationPath', help='use the specified configuration file', metavar='NAME', default=expandBasePath('development.ini'))
    return optionParser


def initialize(options):
    # Show feedback
    print 'Using %s' % options.configurationPath
    # Load
    configuration = ConfigParser.ConfigParser({'here': basePath})
    configuration.read(options.configurationPath)
    # Connect
    model.init_model(sa.create_engine(configuration.get('app:main', 'sqlalchemy.url')))
    # Return
    return configuration, file_store.PathStore(configuration.get('app:main', 'path_storage'))
