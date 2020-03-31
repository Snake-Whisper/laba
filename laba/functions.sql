DROP function IF EXISTS craft_url$$
CREATE FUNCTION craft_url (p_chks TEXT, p_salt CHAR(10), p_data_dir TEXT, p_deep INT)
RETURNS TEXT
BEGIN
	DECLARE v_zaehler INT;
    SET v_zaehler = 0;
    l_fill: WHILE v_zaehler <= p_deep DO
		SELECT INSERT(p_chks, v_zaehler*2, 0, "/") INTO p_chks;
        SET v_zaehler = v_zaehler + 1;
	END WHILE l_fill;
	RETURN CONCAT(p_data_dir, p_chks, p_salt);
END$$

DROP function if exists get_file$$
CREATE FUNCTION get_file (p_id INT, p_data_dir TEXT, p_deep INT)
RETURNS TEXT
BEGIN
	DECLARE v_chks TEXT;
    DECLARE v_salt CHAR(10);
	SELECT chks, salt INTO v_chks, v_salt FROM files WHERE id = p_id;
    RETURN craft_url(v_chks, v_salt, p_data_dir, p_deep);
END$$
