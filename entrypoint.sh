# KEEP IN LF!

#!/bin/sh
cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime

service mariadb start

bash mysql-setup.sh

service cron start
/usr/bin/crontab /etc/cron.d/crontab

apachectl -D FOREGROUND
