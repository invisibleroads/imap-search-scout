#!/usr/local/bin/python2.6


'Reset database'


# Import system modules
# Import custom modules
import script_process
from scout import model
from scout.model import meta
from scout.lib import store


def run():
    # Connect
    meta.metadata.bind = meta.engine
    # Reflect
    meta.metadata.reflect()
    # Clear database
    meta.metadata.drop_all()
    meta.metadata.create_all()
    # Clear folders
    store.removeSafely(pathStore.getDocumentBasePath())
    store.removeSafely(pathStore.getIndexBasePath())
    # Return
    return 'Reset'


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, args = optionParser.parse_args()
    # Initialize
    pathStore = script_process.initialize(options)[1]
    # Run
    print run()
