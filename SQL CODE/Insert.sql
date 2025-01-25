-- Insert data into User table

INSERT INTO User (user_id, password, first_name, last_name, middle_name, gender, address, date_of_birth, phone_number, email) VALUES
('U001', 'password1', 'Alice', 'Johnson', 'M', 'F', '123 Maple St', '1990-05-15', '5551230001', 'alice.j@example.com'),
('U002', 'password2', 'Bob', 'Smith', 'A', 'M', '456 Oak St', '1988-03-20', '5551230002', 'bob.smith@example.com'),
('U003', 'password3', 'Catherine', 'Brown', 'N', 'F', '789 Pine St', '1992-07-11', '5551230003', 'catherine.b@example.com'),
('U004', 'password4', 'David', 'Wilson', 'O', 'M', '101 Cedar St', '1985-12-05', '5551230004', 'david.w@example.com'),
('U005', 'password5', 'Eva', 'Taylor', 'P', 'F', '202 Elm St', '1991-04-14', '5551230005', 'eva.t@example.com'),
('U006', 'password6', 'Frank', 'White', 'Q', 'M', '303 Birch St', '1987-06-23', '5551230006', 'frank.w@example.com'),
('U007', 'password7', 'Grace', 'Harris', 'R', 'F', '404 Willow St', '1993-09-02', '5551230007', 'grace.h@example.com'),
('U008', 'password8', 'Henry', 'Martin', 'S', 'M', '505 Maple St', '1989-11-19', '5551230008', 'henry.m@example.com'),
('U009', 'password9', 'Isabel', 'Clark', 'T', 'F', '606 Oak St', '1994-01-10', '5551230009', 'isabel.c@example.com'),
('U010', 'password10', 'Jack', 'Rodriguez', 'U', 'M', '707 Pine St', '1990-02-25', '5551230010', 'jack.r@example.com');

-- Insert data into OnlineCustomer table
INSERT INTO OnlineCustomer (user_id) VALUES
('U001'), ('U002'), ('U003'), ('U004'), ('U005');

-- Insert data into WalkInCustomer table
INSERT INTO WalkInCustomer (user_id) VALUES
('U006'), ('U007'), ('U008'), ('U009'), ('U010');

-- Insert data into MembershipCard table
INSERT INTO MembershipCard (member_id, user_id, issue_date, expiry_date) VALUES
('M001', 'U006', '2023-01-15', '2024-01-15'),
('M002', 'U007', '2023-02-20', '2024-02-20'),
('M003', 'U008', '2023-03-10', '2024-03-10'),
('M004', 'U009', '2023-04-05', '2024-04-05'),
('M005', 'U010', '2023-05-18', '2024-05-18');

INSERT INTO Employee (employee_id, employee_type, start_date, email, phone_number, password) VALUES
('E001', 'Cashier', '2022-01-10', 'alice.smith@example.com', '123-456-7890', 'password123'),
('E002', 'Floor Staff', '2022-03-15', 'bob.jones@example.com', '234-567-8901', 'password123'),
('E003', 'Manager', '2022-05-20', 'carol.white@example.com', '345-678-9012', 'password123'),
('E004', 'Cashier', '2022-07-25', 'david.brown@example.com', '456-789-0123', 'password123'),
('E005', 'Floor Staff', '2022-09-30', 'eve.johnson@example.com', '567-890-1234', 'password123');

-- Insert data into Store table
INSERT INTO Store (store_id, store_name, address, contact_info) VALUES
('S001', 'Downtown Market', '123 Main St, City A', '123-456-7890'),
('S002', 'Uptown Market', '456 Elm St, City B', '234-567-8901'),
('S003', 'Central Grocery', '789 Maple St, City C', '345-678-9012'),
('S004', 'Northside Supermart', '101 Oak St, City D', '456-789-0123'),
('S005', 'Southside Grocers', '202 Pine St, City E', '567-890-1234');

-- Insert data into ShiftDuty table
INSERT INTO ShiftDuty (record_id, employee_id, store_id, date, working_hour) VALUES
('SD001', 'E001', 'S001', '2024-10-01', 8),
('SD002', 'E002', 'S002', '2024-10-02', 6),
('SD003', 'E003', 'S003', '2024-10-03', 8),
('SD004', 'E004', 'S001', '2024-10-04', 5),
('SD005', 'E005', 'S002', '2024-10-05', 7);

-- Insert data into Voucher table
INSERT INTO Voucher (voucher_id, store_id, issue_date) VALUES
('V001', 'S001', '2024-01-10'),
('V002', 'S002', '2024-02-15'),
('V003', 'S003', '2024-03-20'),
('V004', 'S004', '2024-04-05'),
('V005', 'S005', '2024-05-10');

-- Insert data into Sale table
INSERT INTO Sale (sale_id, store_id, date_of_issue, conditions) VALUES
('SA001', 'S001', '2024-01-15', 'Discount on electronics'),
('SA002', 'S002', '2024-02-20', 'Buy 1 get 1 free on clothes'),
('SA003', 'S003', '2024-03-25', '20% off on home appliances'),
('SA004', 'S004', '2024-04-10', 'Clearance sale on shoes'),
('SA005', 'S005', '2024-05-15', 'Free delivery on orders over $50');

-- Insert data into Aisle table
INSERT INTO Aisle (aisle_number, section) VALUES
('A01', 'Section 1'),
('A02', 'Section 1'),
('A03', 'Section 2'),
('A04', 'Section 2'),
('A05', 'Section 3');

-- Insert data into Product table
INSERT INTO Product (product_id, name, description, unit_price, quantity, product_type) VALUES
('P001', 'Laptop', '15-inch laptop', 1000.00, 10, 'Non-perishable'),
('P002', 'Smartphone', 'Latest model smartphone', 800.00, 15, 'Non-perishable'),
('P003', 'Headphones', 'Noise-cancelling headphones', 150.00, 25, 'Non-perishable'),
('P004', 'Milk', '1 gallon of whole milk', 3.50, 40, 'Perishable'),
('P005', 'Bread', 'Whole grain bread loaf', 2.00, 35, 'Perishable');

-- Insert data into ProductAisleManagement table
INSERT INTO ProductAisleManagement (allocation_id, employee_id, aisle_number, product_id, date_of_allocation) VALUES
('PA001', 'E001', 'A01', 'P001', '2024-01-15'),
('PA002', 'E002', 'A02', 'P002', '2024-02-20'),
('PA003', 'E003', 'A03', 'P003', '2024-03-25'),
('PA004', 'E004', 'A04', 'P004', '2024-04-10'),
('PA005', 'E005', 'A05', 'P005', '2024-05-15');

-- Insert data into Supplier table
INSERT INTO Supplier (supplier_id, supplier_name) VALUES
('S001', 'Tech Suppliers Inc.'),
('S002', 'Furniture World'),
('S003', 'Home Appliances Ltd.'),
('S004', 'Fresh Foods'),
('S005', 'Bakery Supplies');

-- Insert data into ProductSupplier table
INSERT INTO ProductSupplier (supplier_id, product_id) VALUES
('S001', 'P001'),
('S001', 'P002'),
('S002', 'P003'),
('S004', 'P004'),
('S005', 'P005');

-- Insert data into Bill table
INSERT INTO Bill (bill_id, user_id, employee_id, bill_date, bill_amount, payment_method, transaction_id) VALUES
('B001', 'U001', 'E001', '2024-11-01', 120.50, 'Credit Card', 'T001'),
('B002', 'U002', 'E002', '2024-11-02', 75.30, 'Debit Card', 'T002'),
('B003', 'U003', 'E003', '2024-11-03', 250.00, 'Cash', 'T003'),
('B004', 'U004', 'E001', '2024-11-04', 88.90, 'Credit Card', 'T004'),
('B005', 'U005', 'E002', '2024-11-05', 52.40, 'Cash', 'T005');

-- Insert data into Orders table
INSERT INTO Orders (order_num, user_id, order_date, total_amount) VALUES
('O001', 'U001', '2024-11-01', 200.50),
('O002', 'U002', '2024-11-02', 150.30),
('O003', 'U003', '2024-11-03', 340.00),
('O004', 'U004', '2024-11-04', 180.90),
('O005', 'U005', '2024-11-05', 250.00);

-- Insert data into OrderProduct table
INSERT INTO OrderProduct (order_num, product_id, quantity, unit_price) VALUES
('O001', 'P001', 2, 1000.00),
('O001', 'P004', 1, 3.50),
('O002', 'P002', 1, 800.00),
('O003', 'P003', 3, 150.00),
('O004', 'P005', 5, 2.00);