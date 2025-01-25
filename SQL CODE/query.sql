-- Trigger: Prevent deletion of a product if quantity is more than zero
DELIMITER $$

CREATE TRIGGER prevent_product_deletion
BEFORE DELETE ON Product
FOR EACH ROW
BEGIN
    IF OLD.quantity > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete product. Quantity is greater than zero.';
    END IF;
END $$

DELIMITER ;

-- Trigger: Update Product Quantity after a sale
DELIMITER $$

CREATE TRIGGER after_product_sale
AFTER INSERT ON OrderProduct
FOR EACH ROW
BEGIN
    UPDATE Product
    SET quantity = quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END $$

DELIMITER ;

-- Procedure: Add New Product
DELIMITER $$

CREATE PROCEDURE AddNewProduct (
    IN p_product_id VARCHAR(100),
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_unit_price DECIMAL(10, 2),
    IN p_quantity INT,
    IN p_product_type ENUM('Perishable', 'Non-perishable'),
    IN p_aisle_number VARCHAR(100),
    IN p_employee_id VARCHAR(100)
)
BEGIN
    -- Insert Product record
    INSERT INTO Product (product_id, name, description, unit_price, quantity, product_type)
    VALUES (p_product_id, p_name, p_description, p_unit_price, p_quantity, p_product_type);

    -- Allocate product to aisle
    INSERT INTO ProductAisleManagement (allocation_id, employee_id, aisle_number, product_id, date_of_allocation)
    VALUES (UUID(), p_employee_id, p_aisle_number, p_product_id, CURDATE());
END $$

DELIMITER ;

-- Procedure: Add Sale and Update Product Quantity
DELIMITER $$

CREATE PROCEDURE AddSale (
    IN p_user_id VARCHAR(100),
    IN p_employee_id VARCHAR(100),
    IN p_payment_method VARCHAR(50),
    IN p_transaction_id VARCHAR(100),
    IN p_product_id VARCHAR(100),
    IN p_quantity INT
)
BEGIN
    DECLARE v_total_amount DECIMAL(10, 2);
    DECLARE v_unit_price DECIMAL(10, 2);

    -- Get the product price
    SELECT unit_price INTO v_unit_price FROM Product WHERE product_id = p_product_id;

    -- Calculate total sale amount
    SET v_total_amount = v_unit_price * p_quantity;

    -- Insert Sale record
    INSERT INTO Bill (user_id, employee_id, bill_date, bill_amount, payment_method, transaction_id)
    VALUES (p_user_id, p_employee_id, CURDATE(), v_total_amount, p_payment_method, p_transaction_id);

    -- Update Product Quantity
    UPDATE Product
    SET quantity = quantity - p_quantity
    WHERE product_id = p_product_id;

END $$

DELIMITER ;

-- View: Available Products
CREATE VIEW AvailableProducts AS
SELECT
    p.product_id,
    p.name AS product_name,
    p.description,
    p.unit_price,
    p.quantity,
    p.product_type,
    pa.aisle_number
FROM
    Product p
JOIN
    ProductAisleManagement pa ON p.product_id = pa.product_id
WHERE
    p.quantity > 0;

-- View: Sales Summary by Product
CREATE VIEW SalesSummaryByProduct AS
SELECT
    p.product_id,
    p.name AS product_name,
    SUM(op.quantity) AS total_sold,
    SUM(op.quantity * p.unit_price) AS total_revenue
FROM
    OrderProduct op
JOIN
    Product p ON op.product_id = p.product_id
GROUP BY
    p.product_id, p.name;

-- Testing Triggers and Views:
-- 1. Product deletion:
DELETE FROM Product WHERE product_id = 'P001';
-- output  Cannot delete product. Quantity is greater than zero.
UPDATE Product SET quantity = 0 WHERE product_id = 'P001';
DELETE FROM Product WHERE product_id = 'P001';
-- output P001 will be deleted because of trigger which allows to do it after updating quantity.
INSERT INTO Product (product_id, name, description, unit_price, quantity, product_type) VALUES
('P001', 'Laptop', '15-inch laptop', 1000.00, 10, 'Non-perishable');
-- 2. Quantity update after sale
SELECT product_id, quantity FROM Product WHERE product_id = 'P001';
-- output P001,10
-- Now inserting new order into orderproduct table 
INSERT INTO Orders (order_num, user_id, order_date, total_amount)
VALUES ('005', 'U001', '2024-12-01', 100.00);
INSERT INTO OrderProduct (order_num, product_id, quantity, unit_price)
VALUES ('005', 'P001', 8, 20.00);
SELECT product_id, quantity FROM Product WHERE product_id = 'P001';
-- output P001,2 quantity decreased from 10 to 2

-- 3. Add new product
CALL AddNewProduct(
    'P006',
    'Water Bottle',
    'Drinking water case.',
    0.99,
    50,
    'Non-perishable',
    'A01',
    'E005'
);
SELECT * FROM Product WHERE product_id = 'P006';
SELECT * FROM ProductAisleManagement WHERE product_id = 'P006';
-- output new product will be updated on both tables.

 -- 4. Add new sale
 CALL AddSale(
    'U001',
    'E001',
    'Credit Card',
    'txn123',
    'P001',
    3
);
SELECT * FROM Bill WHERE transaction_id = 'txn123';
SELECT product_id, quantity FROM Product WHERE product_id = 'P001';

-- 5. Testing views
SELECT * FROM AvailableProducts;
SELECT * FROM SalesSummaryByProduct;

 



-- Functional Requirements:

-- 1. Add New User
-- The system allows the addition of new users with validation for required fields.

INSERT INTO User (user_id, password, first_name, last_name, middle_name, gender, address, date_of_birth, phone_number, email)
 VALUES ('U011', 'securePass30', 'Emily', 'Johnson', 'U', 'F', '456 Oak Lane', '1995-11-30', '5554567890', 'emily.johnson@example.com'),
		('U012', 'newPass12', 'Michael', 'Smith', 'U', 'M', '789 Birch Road', '1992-06-18', '5552345678', 'michael.smith@example.com');
        
 Select * from user;
 
 -- 2. Classify Customer Types
-- Enable classification of users as Online Customers or Walk-in Customers, storing relevant details.

INSERT INTO OnlineCustomer (user_id)
VALUES ('U011');
-- Add a Walk-in Customer:
INSERT INTO WalkInCustomer (user_id) 
VALUES ('U012');

-- 3. Process Customer Orders
-- The Orders table records detailed information about customer transactions, including a unique order_num, the associated user_id from the user table, the order_date, and the total_amount, enabling efficient tracking and management of online customer orders.
select * from orders;

-- 4. Manage Memberships
-- The MembershipCard table manages the issuance of membership cards, associating each card with a unique member_id, a user_id from the User table, an issue_date, and an expiry_date, allowing for the tracking and management of membership statuses.
select * from membershipcard;

-- 5. Track Employee Information
-- Add and modify employee details.
-- Add an Employee:
INSERT INTO Employee (employee_id, employee_type, start_date, email, phone_number, password) VALUES 
('E006', 'Manager', '2023-03-15', 'jasend@example.com', '678-901-2345', 'securePass456'),
('E007', 'Cashier', '2023-05-10', 'susan.martin@example.com', '789-012-3456', 'strongPassword789');

-- Modify Employee Details:
UPDATE Employee 
SET email = 'new_email@example.com', phone_number = '555-8765' 
WHERE employee_id = 'E007';

-- 6. Schedule Employee Shifts
-- Create and modify employee shift schedules.
-- Add Employee Shift:
INSERT INTO ShiftDuty (record_id, employee_id, store_id, date, working_hour) VALUES
('SD006', 'E006', 'S003', '2024-10-03', 7),
('SD007', 'E007', 'S002', '2024-10-04', 5);

-- Modify Employee Shift:
UPDATE ShiftDuty 
SET working_hour = 9 
WHERE employee_id = 'E006' AND date = '2024-10-03';
select * from ShiftDuty;

-- 7. Store Information Management
-- Add and modify store details.
-- Add a Store:
INSERT INTO Store (store_id, store_name, address, contact_info) 
VALUES ('S006', 'Downtown Store', '456 Elm Street', '555-1122');

-- Modify Store Details:
UPDATE Store 
SET contact_info = '555-3344' 
WHERE store_id = 'S004';

-- 8. Issue and Manage Vouchers
-- Issue Voucher:

INSERT INTO Voucher (voucher_id, store_id, issue_date) 
VALUES ('V006', 'S006', '2024-11-27');
select * from voucher;

--  9. Record Sales Transactions
-- Entry and management of sales records.

INSERT INTO Sale (sale_id, store_id, conditions, date_of_issue) 
VALUES ('SA006', 'S006', 'Black Friday Sale', '2024-11-27');
select * from sale;

-- 10. Manage Product and Aisle Allocation
-- Enables product-to-aisle allocation.
select * from productaislemanagement;

-- 11. Track Suppliers and Products
-- Manage supplier details and their associated products.
-- Add Supplier:

INSERT INTO Supplier (supplier_id, supplier_name) VALUES
('S006', 'Best Suppliers Inc.');

-- Add Product from Supplier:
INSERT INTO Product (product_id, name, description, unit_price, quantity, product_type) VALUES
('P006', 'Apple', 'Fresh Red Apple', 100, 1.50, 'Perishable');

-- Tracking
INSERT INTO ProductSupplier (supplier_id, product_id) VALUES
('S006', 'P006');

-- 12. Generate Billing Records
-- The Bill table records billing transactions by linking each transaction to a specific user_id and employee_id, while capturing the bill_date, bill_amount, payment_method, and a unique transaction_id for each sale.
Select * from bill;

-- Other Queries implementing the functional Requirements:

--  Retrieve a list of all online customers who have placed an order:
SELECT DISTINCT u.user_id, u.first_name, u.last_name, u.email
FROM User u
JOIN OnlineCustomer o ON u.user_id = o.user_id
JOIN Orders ord ON u.user_id = ord.user_id;

-- Find all customers who have a membership card:

SELECT u.first_name, u.last_name, u.email
FROM User u
JOIN MembershipCard mc ON u.user_id = mc.user_id;

-- Get the most popular product (the one sold the most):

SELECT p.name, SUM(op.quantity) AS total_sold
FROM Product p
JOIN OrderProduct op ON p.product_id = op.product_id
GROUP BY p.product_id
ORDER BY total_sold DESC
LIMIT 1;

-- Retrieve a list of products with low stock (e.g., quantity less than 5):

SELECT p.name, p.quantity
FROM Product p
WHERE p.quantity < 10;

--  Retrieve a list of all vouchers issued by a specific store:

SELECT v.voucher_id, v.issue_date
FROM Voucher v
WHERE v.store_id = 'S001';

-- Get all orders placed by a specific customer:

SELECT o.order_num, o.order_date, o.total_amount
FROM Orders o
WHERE o.user_id = 'U001';

-- Find all sales that were subject to a particular promotion:

SELECT s.store_name, sa.conditions, sa.date_of_issue
FROM Sale sa
JOIN Store s ON sa.store_id = s.store_id
WHERE sa.conditions LIKE '%20% off%';

-- List all employees who have worked at a particular store on a given date:

SELECT DISTINCT e.employee_id, e.employee_type, e.start_date
FROM Employee e
JOIN ShiftDuty sd ON e.employee_id = sd.employee_id
WHERE sd.store_id = 'S002' AND sd.date = '2024-10-02';

-- Get a list of all the products allocated to a specific aisle:

SELECT p.name, p.description, p.unit_price, p.quantity
FROM Product p
JOIN ProductAisleManagement pam ON p.product_id = pam.product_id
WHERE pam.aisle_number = 'A01';

-- Get all employees working in a specific store on a given date:

SELECT e.employee_id, e.employee_type, e.email, e.phone_number
FROM Employee e
JOIN ShiftDuty sd ON e.employee_id = sd.employee_id
WHERE sd.store_id = 'S001' AND sd.date = '2024-10-01';

-- Find the employees who have worked the most hours at a store in a given month:

SELECT e.employee_id, e.employee_type, SUM(sd.working_hour) AS total_hours
FROM Employee e
JOIN ShiftDuty sd ON e.employee_id = sd.employee_id
WHERE sd.date BETWEEN '2024-10-01' AND '2024-10-31'
GROUP BY e.employee_id
ORDER BY total_hours DESC
LIMIT 1;