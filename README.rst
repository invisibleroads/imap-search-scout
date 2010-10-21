IMAP email search and storage system
====================================

Installation on Fedora
----------------------
Install libraries
::

    su
        yum -y install git python-setuptools python-setuptools-devel xapian-bindings-python
        easy_install -U pylons sqlalchemy recaptcha-client

Setup development server
::

    git clone git://github.com/invisibleroads/imap-search-scout.git
    cd imap-search-scout
    paster setup-app development.ini
    paster serve --reload development.ini

Setup production server
::

    su
        # Setup packages
        yum -y remove httpd
        yum -y install nginx postgresql-server python-psycopg2
        # Start services
        service nginx start
        service postgresql initdb
        service postgresql start
        # Prepare database
        createdb scout
        # Deploy code
        mkdir -p /var/www/scout
        git clone git://github.com/invisibleroads/imap-search-scout.git /var/www/scout
        cd /var/www/scout
        paster make-config scout production.ini
        paster setup-app production.ini
        crontab crontab.crt
        # Point nginx to paster
        vim /etc/nginx/nginx.conf
        # Open port 80 in firewall
        system-config-firewall
