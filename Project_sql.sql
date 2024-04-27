--Table Creation
CREATE TABLE users(
	u_id SERIAL PRIMARY KEY,
	name TEXT,
	passwd TEXT,
	email TEXT UNIQUE NOT NULL,
	phone TEXT,
	is_manager BOOLEAN NOT NULL
);

CREATE TABLE items(
	i_id SERIAL PRIMARY KEY,
	name TEXT,
	descrip TEXT,
	price INT,
	stock INT
);

CREATE TABLE purchases(
	p_id SERIAL PRIMARY KEY,
	i_id INT NOT NULL,
	u_id INT NOT NULL,
	quantity INT NOT NULL,
	is_done BOOLEAN NOT NULL,
	created TIMESTAMP,
	FOREIGN KEY(i_id) REFERENCES items(i_id),
	FOREIGN KEY(u_id) REFERENCES users(u_id)
);

CREATE OR REPLACE PROCEDURE new_user(
	n_name TEXT,
	n_email TEXT,
	n_passwd TEXT,
	n_phone TEXT,
	status BOOLEAN
)
language plpgsql
AS $$
BEGIN
INSERT INTO users(name, email, passwd, phone, is_manager) VALUES (n_name, n_email, n_passwd, n_phone, status);
END;$$

CREATE OR REPLACE PROCEDURE new_item(
	n_name TEXT,
	n_descrip TEXT,
	n_price INT,
	n_stock INT
)
language plpgsql
AS $$
BEGIN
INSERT INTO items(name, descrip, price, stock) VALUES (n_name, n_descrip, n_price, n_stock);
END;$$


CREATE OR REPLACE PROCEDURE new_purchase(
	n_u_id INT,
	n_i_id INT,
	n_quantity INT
)
language plpgsql
AS $$
BEGIN
INSERT INTO purhases(u_id, i_id, quantity, is_done, created) VALUES (n_u_id, n_i_id, n_quantity, false, CURRENT_TIMESTAMP(0));
END;$$

CREATE OR REPLACE FUNCTION authenticate(
	n_email TEXT,
	n_passwd TEXT
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
	result_id INT;
BEGIN
	SELECT u_id FROM users
	INTO result_id
	WHERE email = n_email AND passwd = n_passwd;
	IF FOUND THEN
	RETURN result_id;
	ELSE
	RETURN -1;
	END IF;
END;$$

CALL new_user('admin', 'admin', 'admin', '0300-0000000', true);

