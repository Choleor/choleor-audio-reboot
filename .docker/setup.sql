-- UPDATE mysql.user
-- 	set authentication_string=PASSWORD("dkmysqlaudioroot"),
-- 	password_expired='N',
-- 	plugin='mysql_native_password',
-- 	host='root'
-- where User='root';
CREATE USER 'django'@'%' IDENTIFIED BY 'dkmysqlaudio';
CREATE DATABASE 'choleor_audio' IF NOT EXISTS;
USE choleor_audio;
GRANT ALL PRIVILEGES ON *.* TO 'django'@'%';
FLUSH PRIVILEGES;