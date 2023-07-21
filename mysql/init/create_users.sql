CREATE database decidir;

USE decidir;

CREATE TABLE users (
  user_id bigint NOT NULL,
  signup_at varchar(20) DEFAULT NULL,
  platform varchar(20) DEFAULT NULL,
  user_address varchar(50) DEFAULT NULL,
  user_name varchar(200) NOT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;