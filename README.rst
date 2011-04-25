scout
===========
::

    # Activate isolated environment
    source ../../bin/activate
    # Install dependencies
    python setup.py develop
    # Run tests with coverage
    nosetests
    # Show URL routes
    paster proutes development.ini scout
    # Run shell
    paster pshell development.ini scout
    # Start server
    paster serve --reload development.ini
