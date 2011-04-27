IMAP email search and storage system
====================================


Installation
-------------
::
 
    # Prepare isolated environment
    PYRAMID_ENV=$HOME/pyramid-env
    virtualenv --no-site-packages $PYRAMID_ENV 
    # Activate isolated environment
    source $PYRAMID_ENV/bin/activate
    # Clone repository
    PROJECTS=$HOME/Projects
    mkdir $PROJECTS
    cd $PROJECTS
    git clone git://github.com/invisibleroads/imap-search-scout.git
    # Enter repository
    cd $PROJECTS/imap-search-scout
    # Install dependencies
    python setup.py develop
 
 
Usage
-----
::

    # Activate isolated environment
    source $PYRAMID_ENV/bin/activate
    # Enter repository
    cd $PROJECTS/imap-search-scout
    # Run tests with coverage
    nosetests
    # Show URL routes
    paster proutes development.ini scout
    # Run shell
    paster pshell development.ini scout
    # Start server
    paster serve --reload development.ini
