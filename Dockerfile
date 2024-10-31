FROM ubuntu:24.04

WORKDIR /root 

COPY entrypoint.sh entrypoint.sh
COPY mysql-setup.sh mysql-setup.sh
RUN chmod 0777 entrypoint.sh
RUN chmod 0777 mysql-setup.sh

RUN apt update && apt -y upgrade
RUN apt install -y unzip wget

RUN apt install python3-full -y
RUN apt install -y pip

COPY main.py main.py
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt --break-system-packages

RUN apt install -y mariadb-server
RUN apt install -y apache2

RUN apt install -y software-properties-common
RUN add-apt-repository ppa:ondrej/php
RUN apt update
RUN apt install -y php7.4 php7.4-mysqli php7.4-mbstring php7.4-ctype php7.4-xml php7.4-json php7.4-zip php7.4-gd php7.4-imagick php7.4-intl php7.4-bcmath

RUN rm /var/www/html/index.html
RUN wget https://files.phpmyadmin.net/phpMyAdmin/5.2.1/phpMyAdmin-5.2.1-all-languages.zip
RUN unzip phpMyAdmin-5.2.1-all-languages.zip
RUN mv phpMyAdmin-5.2.1-all-languages/* /var/www/html
RUN rm phpMyAdmin-5.2.1-all-languages.zip
COPY config.inc.php /var/www/html/config.inc.php
RUN rm /var/www/html/config.sample.inc.php

RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 0744 /var/www/html

RUN apt install -y cron
COPY crontab /etc/cron.d/crontab
RUN chmod 0600 /etc/cron.d/crontab

EXPOSE 80/tcp

CMD ["bash", "entrypoint.sh"]