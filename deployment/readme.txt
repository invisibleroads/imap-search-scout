yum install xapian-bindings-python
yum install zlib-devel
yum install python-setuptools python-setuptools-devel
yum install postgresql-server python-psycopg2
yum install python-cjson
easy_install pylons sqlalchemy

# Enable and start httpd or nginx service
# Enable and start postgresql service
# Deactivate SELinux
# Open port 80 in firewall

setup storage folder
setup /var/www/pylons
install scout
edit httpd.conf or nginx.conf to setup mod_proxy for paster
mkdir /var/www/pylons/scout/logs
createdb scout
python utilities/reset.py -c utilities/remote/production.ini

create /var/www/pylons/scout/.people.cfg
python utilities/setup.py -c utilities/remote/production.ini

setup cronjob for python utilities/archive.py -c utilities/remote/production.ini
crontab crontab.crt

edit .production.cfg using default.cfg
