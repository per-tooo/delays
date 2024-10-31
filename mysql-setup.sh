# KEEP IN LF!

mysql -u root -e \
  "
    CREATE USER IF NOT EXISTS 'delays'@'localhost' IDENTIFIED BY 'test';
    CREATE DATABASE IF NOT EXISTS delays;
    GRANT ALL PRIVILEGES ON delays.* TO 'delays'@'localhost';
    FLUSH PRIVILEGES;
  "
