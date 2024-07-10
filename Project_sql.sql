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
INSERT INTO purchases(u_id, i_id, quantity, is_done, created) VALUES (n_u_id, n_i_id, n_quantity, false, CURRENT_TIMESTAMP(0));
UPDATE items SET stock = stock - n_quantity WHERE i_id = n_i_id;
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

CALL new_user('customer', 'customer', 'customer', '0300-0000000', false);

CREATE OR REPLACE FUNCTION check_valid_user(
	n_email TEXT
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
	result_id INT;
BEGIN
	SELECT u_id FROM users
	INTO result_id
	WHERE email = n_email;
	IF FOUND THEN
	RETURN 0;
	ELSE
	RETURN 1;
	END IF;
END;$$

SELECT * FROM check_valid_user('admin');

CREATE OR REPLACE FUNCTION check_manager(
	auth_id INT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
	result_m BOOLEAN;
BEGIN
	SELECT is_manager FROM users
	INTO result_m
	WHERE u_id = auth_id;
	RETURN result_m;
END;$$

DROP FUNCTION check_manager;

SELECT * FROM check_manager(1);

CALL new_item('Sports Shoes', 'Power through your workouts with our selection of sport shoes! Designed for comfort and performance, these shoes provide the support and flexibility you need to conquer any activity. Whether you''re hitting the gym, court, or track, find the perfect pair to help you reach your fitness goals.', 9000, 40);
CALL new_item('Swimming Goggles', 'Dive into comfort and clarity with our high-performance swimming goggles! Featuring a leak-proof seal and wide range of vision, these goggles will keep your eyes protected and focused underwater. Perfect for lap swimmers, recreational enthusiasts, or anyone who wants to enjoy the pool without irritation. ', 2500, 22);

SELECT i_id, name, descrip, price, stock FROM items;

SELECT i_id, name, descrip, price, stock FROM items WHERE i_id=1;

CREATE OR REPLACE PROCEDURE update_item(
	n_i_id INT,
	n_name TEXT,
	n_descrip TEXT,
	n_price INT,
	n_stock INT
)
language plpgsql
AS $$
BEGIN
UPDATE items SET name = n_name, descrip = n_descrip, price = n_price, stock = n_stock WHERE i_id = n_i_id;
END;$$

CREATE OR REPLACE VIEW completed_records AS
SELECT p_id, u.name u_name, u.email u_email, u.phone u_phone, i.name i_name, quantity, created
FROM purchases
JOIN users u ON purchases.u_id = u.u_id
JOIN items i ON purchases.i_id = i.i_id
WHERE is_done = true
ORDER BY created DESC;

CREATE OR REPLACE VIEW remaining_records AS
SELECT p_id, u.name u_name, u.email u_email, u.phone u_phone, i.name i_name, quantity, created
FROM purchases
JOIN users u ON purchases.u_id = u.u_id
JOIN items i ON purchases.i_id = i.i_id
WHERE is_done = false
ORDER BY created ASC;

DROP VIEW remaining_records;

SELECT * FROM completed_records;

SELECT * FROM remaining_records;

CREATE OR REPLACE FUNCTION check_record(
	c_id INT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
if_exist BOOLEAN;
BEGIN
SELECT EXISTS(SELECT * FROM purchases WHERE c_id = p_id AND is_done = false) INTO if_exist;
IF if_exist THEN
UPDATE purchases SET is_done = true WHERE p_id = c_id;
END IF;
RETURN if_exist;
END;$$

SELECT * FROM check_record(1);

CREATE TABLE images(
	img_id SERIAL PRIMARY KEY,
	i_id INT,
	img_name TEXT,
	FOREIGN KEY(I_ID) REFERENCES items(i_id)
);

CREATE FUNCTION img_upload(
	_i_id integer,
	_exten text)
RETURNS text
LANGUAGE 'plpgsql'
AS $$
DECLARE
	_img_name TEXT;
	_img_id INT;
BEGIN
	INSERT INTO images(i_id) VALUES (_i_id) RETURNING img_id INTO _img_id;
	_img_name := CONCAT(_IMG_ID, '.', _exten);
	UPDATE images SET img_name = _img_name WHERE img_id  = _img_id;
	RETURN _img_name;
END;$$

CREATE FUNCTION get_img(
	_i_id INT
)
RETURNS TABLE(
	_img_id INT,
	_img_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
RETURN QUERY
SELECT img_id, img_name FROM images WHERE i_id = _i_id;
END;$$

SELECT * FROM get_img(2);

CREATE FUNCTION delete_img(
	_img_id INT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
	_img_name TEXT;
BEGIN
	SELECT img_name FROM images INTO _img_name WHERE img_id = _img_id;
	DELETE FROM images WHERE img_id = _img_id;
	RETURN _img_name;
END;$$
