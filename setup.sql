CREATE DATABASE forbes_app;
CREATE USER 'forbes_app'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON forbes_app.* TO 'forbes_app'@'localhost';
FLUSH PRIVILEGES;