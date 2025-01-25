from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class MembershipCard(db.Model):
    __tablename__ = 'MembershipCard'
    member_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('User.user_id'))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)

    user = db.relationship("User", back_populates="membership_card")

    def __repr__(self):
        return f"<MembershipCard {self.member_id}>"

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    user_id = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    address = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)

    membership_card = db.relationship("MembershipCard", back_populates="user")

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"<User {self.user_id}>"

class OnlineCustomer(db.Model):
    __tablename__ = 'OnlineCustomer'
    user_id = db.Column(db.String(100), db.ForeignKey('User.user_id',ondelete="CASCADE"), primary_key=True)
    user = db.relationship("User", backref=db.backref("online_customer", cascade="all, delete", passive_deletes=True))

    def __repr__(self):
        return f"<OnlineCustomer {self.user_id}>"

class WalkInCustomer(db.Model):
    __tablename__ = 'WalkInCustomer'
    user_id = db.Column(db.String(100), db.ForeignKey('User.user_id'), primary_key=True)
    user = db.relationship("User", backref="walkin_customer")

    def __repr__(self):
        return f"<WalkInCustomer {self.user_id}>"


class Employee(db.Model, UserMixin):
    __tablename__ = 'Employee'
    employee_id = db.Column(db.String(100), primary_key=True)
    employee_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    email_address = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    password = db.Column(db.String(100), nullable=False)

    # Relationship with ShiftDuty
    shift_duties = db.relationship("ShiftDuty", back_populates="employee")

    def get_id(self):
        return self.employee_id

    def __repr__(self):
        return f"<Employee {self.employee_id}>"


class ShiftDuty(db.Model):
    __tablename__ = 'ShiftDuty'
    record_id = db.Column(db.String(100), primary_key=True)
    employee_id = db.Column(db.String(100), db.ForeignKey('Employee.employee_id'))
    store_id = db.Column(db.String(100), db.ForeignKey('Store.store_id'))
    date = db.Column(db.Date)
    working_hour = db.Column(db.Integer)

    # Relationships
    employee = db.relationship("Employee", back_populates="shift_duties")
    store = db.relationship("Store", back_populates="shift_duties")

    def __repr__(self):
        return f"<ShiftDuty {self.record_id}>"
    


class Order(db.Model):
    __tablename__ = 'Orders'
    order_num = db.Column(db.String(100), primary_key=True)
    order_date = db.Column(db.Date)
    total_amount = db.Column(db.Numeric(10, 2))
    user_id = db.Column(db.String(100), db.ForeignKey('OnlineCustomer.user_id'))
    order_products = db.relationship('OrderProduct', back_populates='order')

class Product(db.Model):
    __tablename__ = 'Product'
    product_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    unit_price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer)
    product_type = db.Column(db.Enum('Perishable', 'Non-perishable'))
    suppliers = db.relationship('Supplier', secondary='ProductSupplier', back_populates='products')
    order_products = db.relationship('OrderProduct', back_populates='product')

class OrderProduct(db.Model):
    __tablename__ = 'OrderProduct'
    order_num = db.Column(db.String(100), db.ForeignKey('Orders.order_num'), primary_key=True)
    product_id = db.Column(db.String(100), db.ForeignKey('Product.product_id'), primary_key=True)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    order = db.relationship('Order', back_populates='order_products')
    product = db.relationship('Product', back_populates='order_products')

class Sale(db.Model):
    __tablename__ = 'Sale'
    sale_id = db.Column(db.String(100), primary_key=True)
    store_id = db.Column(db.String(100), db.ForeignKey('Store.store_id'))
    date_of_issue = db.Column(db.Date)
    conditions = db.Column(db.Text)

    def __repr__(self):
        return f"<Sale {self.sale_id}, {self.conditions}>"

class Supplier(db.Model):
    __tablename__ = 'Supplier'
    supplier_id = db.Column(db.String(100), primary_key=True)
    supplier_name = db.Column(db.String(100))

    products = db.relationship('Product', secondary='ProductSupplier', back_populates='suppliers')


class ProductSupplier(db.Model):
    __tablename__ = 'ProductSupplier'
    supplier_id = db.Column(db.String(100), db.ForeignKey('Supplier.supplier_id'), primary_key=True)
    product_id = db.Column(db.String(100), db.ForeignKey('Product.product_id'), primary_key=True)



class Store(db.Model):
    __tablename__ = 'Store'
    store_id = db.Column(db.String(100), primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(15))

    # Relationship with ShiftDuty
    shift_duties = db.relationship("ShiftDuty", back_populates="store")

    def __repr__(self):
        return f"<Store {self.store_id}>"