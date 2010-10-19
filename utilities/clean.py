#!/usr/local/bin/python2.6


'Clean database'


# Import system modules
import xapian
# Import custom modules
import script_process
from scout import model
from scout.model import meta


# If we are running the command as a script,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, args = optionParser.parse_args()
    # Initialize
    pathStore = script_process.initialize(options)[1]
    # Clean
    try:
        print model.clean(pathStore, isThorough=True)
    except xapian.DatabaseLockError:
        pass
    else:
        meta.Session.commit()
