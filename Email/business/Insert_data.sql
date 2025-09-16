-- -- SQLite
-- INSERT INTO employees (emp_id, name, device)
-- VALUES
-- ('22615833', 'Ngô Dung', '9PAM7DIFW87DOBEU'),
-- ('22616467', 'Hoàng Linh', 'TSPNH6GYZLPJBY6X'),
-- ('22636101', 'Lê Thùy', 'DEVICE_ID_LE_THUY'),
-- ('22789191', 'Nhàn', 'F6NZ5LRKWWGACYQ8'),
-- ('22814414', 'Bích Ngọc', 'Z5LVOF4PRGXGTS9H'),
-- ('22833463', 'Lưu Thư', 'QK8TEMKZMBYHPV6P'),
-- ('22889226', 'Ngọc Hà', 'DEVICE_ID_NGOC_HA'),
-- ('22894754', 'Hải Yến', '8HMN4T9575HAQWLN'),
-- ('22889521', 'Ngọc Mai', 'PN59BMHYPFXCPN8T'),
-- ('22614471', 'Hoàng Khoa', 'CEIN4X45I7ZHFEFU'),
-- ('22896992', 'Huyền Trang', 'EY5H9DJNIVNFH6OR');




-- INSERT INTO customers (emp_id, customer_email, sent, date,subject,content)
-- VALUES
-- ('22615833', 'newcustomer1@gmail.com', 1, '2025-09-09', 'test subject','test_content'),
-- ('22616467', 'newcustomer2@gmail.com', 1, '2025-09-09', 'test subject','test_content'),
-- ('22636101', 'lethuy_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22789191', 'nhan_customer1@gmail.com', 1, '2025-09-09', 'test subject','test_content'),
-- ('22814414', 'bichngoc_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22833463', 'luuthu_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22889226', 'ngocha_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22894754', 'haiyen_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22889521', 'ngocmai_customer1@gmail.com', 1, '2025-09-09','test subject','test_content'),
-- ('22614471', 'ngocmai_customer1@gmail.com', 1, '2025-09-09','test subject','test_content');
-- ('22896992', 'huyentrang_customer1@gmail.com','1', '2025-09-09','test subject','test_content');


-- -- Insert data into email_accounts table
INSERT INTO email_accounts (emp_id, email_account, num_sent)
VALUES
-- ('22616467', 'hoanglinh.tuyendung1@gmail.com', 3),
-- ('22616467', 'linhphnguyen.timviec365@gmail.com', 3),
-- ('22616467', 'linhphnguyen1.timviec365@gmail.com', 1),
-- ('22616467', 'linhphnguyen2.timviec365@gmail.com', 0),
-- ('22616467', 'linhphnguyen3.timviec365@gmail.com', 0),
-- ('22616467', 'linhphnguyen4.timviec365@gmail.com', 0),
-- ('22616467', 'linhphnguyen5.timviec365@gmail.com', 0),
-- ('22616467', 'phlyv01.timviec365@gmail.com', 0),
-- ('22789191', 'nhanlai02071997@gmail.com', 0),
-- ('22789191', 'linhnguyn.timviec365@gmail.com', 0),
-- ('22789191', 'linhngp.timviec365@gmail.com', 0),
-- ('22789191', 'linhnguyen1.timviec365@gmail.com', 0),
-- ('22789191', 'linhnp4.timviec365@gmail.com', 0),
-- ('22789191', 'linhnp5.timviec365@gmail.com', 0),
-- ('22814414', 'ngocvee365.vn@gmail.com', 3),
-- ('22814414', 'lyphgvu02.timviec365@gmail.com', 0),
-- ('22814414', 'lyphgvu03.timviec365@gmail.com', 0),
-- ('22814414', 'lyphgvu04.timviec365@gmail.com', 0),
-- ('22814414', 'lyphgvu05.timviec365@gmail.com', 0),
-- ('22814414', 'lyphgvu06.timviec365@gmail.com', 0),
-- ('22814414', 'lyphgvu07.timviec365@gmail.com', 0),
-- ('22833463', 'luuthutimviec365@gmail.com', 3),
-- ('22833463', 'lyvup01.timviec365@gmail.com', 3),
-- ('22833463', 'lyvup02.timviec365@gmail.com', 3),
-- ('22833463', 'lyvup03.timviec365@gmail.com', 3),
-- ('22833463', 'lyvup04.timviec365@gmail.com', 3),
-- ('22889521', 'hmaiii0909@gmail.com', 3),
-- ('22889521', 'linhnguyenphg.timviec365@gmail.com', 3),
-- ('22889521', 'linhphg03.tuyendung@gmail.com', 0),
-- ('22889521', 'phuonglinh5.timviec365@gmail.com', 0),
-- ('22889521', 'linhphuong05.timviec365@gmail.com', 0),
-- ('22889521', 'linhnp7.timviec365@gmail.com', 0),
-- ('22889521', 'nhangan366@gmail.com', 0),
-- ('22889521', 'anhng3331@gmail.com', 0),
-- ('22889521', 'manle88711@gmail.com', 0),
-- ('22614471', 'hk0662054@gmail.com', 3),
-- ('22614471', 'bhuy46455@gmail.com', 3),
-- ('22614471', 'ghuy82067@gmail.com', 0),
-- ('22614471', 'lyvp01.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp02.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp03.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp04.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp05.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp06.timviec365@gmail.com', 0),
-- ('22614471', 'lyvp07.timviec365@gmail.com', 0),
-- ('22614471', 'ctyhungha365@gmail.com', 0);
-- ('22896992','huyentrangtimviec3655@gmail.com',0),
-- ('22896992','duongloan036@gmail.com',0),
-- ('22896992','tanhong6833o@gmail.com',0),
-- ('22896992','langh5648@gmail.com',0),
-- ('22896992','phglinh01.timviec365@gmail.com',0),
-- ('22896992','linhphtimviec365@gmail.com',0),
-- ('22896992','phuonglinh03.timviec365@gmail.com',0),
-- ('22896992','linhphuong03.timviec365@gmail.com',0),
-- ('22896992','linhnp3.timviec365@gmail.com',0),
-- ('22896992','maihoavu425@gmail.com',0),
-- ('22896992','oanhha556333@gmail.com',0),
-- ('22896992','hthaolinh91@gmail.com',0),
-- ('22896992','tranghuyen365vn@gmail.com',0),
-- ('22896992','hothuloan257@gmail.com',0),
-- ('22894754','haiyentimviec365@gmail.com',3),
-- ('22894754','yenhoangtimviec365@gmail.com',0),
-- ('22894754','yenytimviec365@gmail.com',0),
-- ('22894754','hyentd365@gmail.com',0),
-- ('22894754','yenhoanghai203@gmail.com',0),
-- ('22894754','lyvu01.timviec365@gmail.com',0),
-- ('22894754','lyvu02.timviec365@gmail.com',0),
-- ('22894754','lyvu03.timviec365@gmail.com',0),
-- ('22894754','lyvu04.timviec365@gmail.com',0),
-- ('22894754','lyvu05.timviec365@gmail.com',0),
-- ('22894754','lyvu06.timviec365@gmail.com',0);
-- ('22615833','quynhdiepn8@gmail.com',0),
-- ('22615833','tranhaily138@gmail.com',0),
-- ('22615833','hoaianlee3030@gmail.com',0),
-- ('22615833','nguyenphuongnga040@gmail.com',0),
-- ('22615833','gialinhle348@gmail.com',0),
-- ('22615833','ngongocduc721@gmail.com',0),





-- UPDATE customers
-- SET sent = 1
-- WHERE customer_id = 12

UPDATE employees
VALUES 

ALTER TABLE employees ADD COLUMN brand TEXT;
UPDATE employees SET brand = 'Redmi';


INSERT INTO employees (emp_id, name, device, brand)
VALUES ('22616467', 'Hoàng Linh', 'EM4DYTEITCCYJNFU', 'Redmi');