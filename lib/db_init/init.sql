create database whois;
create database ranking;

GRANT ALL ON whois.* TO 'bgp-ranking'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON ranking.* TO 'bgp-ranking'@'localhost';
