from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, OnlineCustomer, WalkInCustomer, Employee, Order, OrderProduct, Product, Sale, MembershipCard, ShiftDuty, Store, Supplier
from datetime import datetime
from config import Config  # Import Config class
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config.from_object(Config)  # Load configuration from Config class in config.py

# Initialize SQLAlchemy with the app
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    return Employee.query.get(user_id)

@app.route('/')
def home(): 
    return render_template('home.html')


@app.route('/membership')
@login_required
def membership():
    membership_card = MembershipCard.query.filter_by(user_id=current_user.user_id).first()
    return render_template('membership.html', membership_card=membership_card)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user is an online customer
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            # Set role for the session as 'Customer'
            user.role = 'Customer'
            return redirect(url_for('dashboard'))
        
        # Check if user is an employee
        employee = Employee.query.filter_by(email_address=email).first()
        if employee and employee.password == password:
            login_user(employee)
            # Set role for the session as 'Employee'
            employee.role = 'Employee'
            return redirect(url_for('employee_dashboard'))

        flash('Invalid credentials. Please try again.')
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        
        new_user = User(user_id=user_id, password=password, email=email, first_name=first_name)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "register_success")
            #return redirect(url_for('login'))

            new_online_customer = OnlineCustomer(user_id=user_id)
            db.session.add(new_online_customer)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("User ID or email already exists. Please try a different one.", "register_error")
    
    return render_template('register.html')


@app.route('/view_order_details/<order_num>', methods=['GET'])
@login_required
def view_order_details(order_num):
    # Fetch the order and associated products
    order = Order.query.get(order_num)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for('view_orders'))

    order_items = OrderProduct.query.filter_by(order_num=order_num).all()

    return render_template('order_details.html', order=order, order_items=order_items)



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/employee_dashboard')
@login_required
def employee_dashboard():
    # Check if the current user is an Employee instance
    if hasattr(current_user, 'employee_id'):
        shifts = ShiftDuty.query.filter_by(employee_id=current_user.employee_id).all()
        return render_template('employee_dashboard.html', shifts=shifts)
    else:
        # Handle if somehow accessed by non-employee or redirect
        return redirect(url_for('login'))
   


@app.route('/search_orders', methods=['GET'])
def search_orders():
    search_query = request.args.get('search_query', '').strip()
    
    # Query orders and join with User for customer details
    if search_query:
        orders = Order.query.join(User, Order.user_id == User.user_id).filter(
            (Order.order_num.ilike(f"%{search_query}%")) |
            (User.first_name.ilike(f"%{search_query}%")) |
            (User.last_name.ilike(f"%{search_query}%"))
        ).all()
    else:
        orders = Order.query.join(User, Order.user_id == User.user_id).all()
    
    # Prepare order data for template rendering
    order_data = []
    for order in orders:
        customer = User.query.get(order.user_id)  # Fetch the User linked by user_id
        customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown Customer"
        order_data.append({
            "order_num": order.order_num,
            "order_date": order.order_date,
            "total_amount": order.total_amount,
            "customer_name": customer_name
        })
    
    return render_template('search_orders.html', orders=order_data)




@app.route('/add_shift_duty', methods=['GET', 'POST'])
@login_required
def add_shift_duty():
    if request.method == 'POST':
        # Logic to add shift duty details
        employee_id = request.form['employee_id']
        store_id = request.form['store_id']
        date = request.form['date']
        working_hour = request.form['working_hour']
        
        new_shift_duty = ShiftDuty(
            employee_id=employee_id,
            store_id=store_id,
            date=date,
            working_hour=working_hour
        )
        db.session.add(new_shift_duty)
        db.session.commit()
        flash('Shift duty added successfully', 'success')
        return redirect(url_for('employee_dashboard'))
    return render_template('add_shift_duty.html')


@app.route('/view_shift_duties/<employee_id>')
@login_required
def view_shift_duties(employee_id):
    shifts = ShiftDuty.query.filter_by(employee_id=employee_id).all()
    return render_template('view_shift_duties.html', shifts=shifts)


@app.route('/search_products', methods=['GET'])
def search_products():
    search_query = request.args.get('search_query', '').strip()
    
    if search_query:
        # If a search query is provided, filter products by name or description
        products = Product.query.filter(
            (Product.name.ilike(f"%{search_query}%")) |
            (Product.description.ilike(f"%{search_query}%"))
        ).all()
    else:
        # If no search query is provided, retrieve all products
        products = Product.query.all()
    
    return render_template('search_products.html', products=products)



# Updated route for Customer Management
@app.route('/search_customers', methods=['GET'])
def search_customers():
    search_query = request.args.get('search_query', '').strip()
    
    if search_query:
        # Perform search by name or ID
        customers = User.query.filter(
            (User.first_name.ilike(f"%{search_query}%")) |
            (User.last_name.ilike(f"%{search_query}%")) |
            (User.user_id.ilike(f"%{search_query}%"))
        ).all()
    else:
        # Display all customers if no search query is provided
        customers = User.query.all()
    
    return render_template('employee_dashboard.html', customers=customers)


@app.route('/view_customer/<user_id>')
@login_required
def view_customer(user_id):
    customer = User.query.get_or_404(user_id)
    return render_template('view_customer.html', customer=customer)

@app.route('/edit_customer/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(user_id):
    customer = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Update fields based on form data
        customer.first_name = request.form['first_name']
        customer.last_name = request.form['last_name']
        customer.email = request.form['email']
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('employee_dashboard'))
    return render_template('edit_customer.html', customer=customer)

# Order Management
@app.route('/view_order/<order_num>')
@login_required
def view_order(order_num):
    order = Order.query.get_or_404(order_num)
    order_items = OrderProduct.query.filter_by(order_num=order_num).all()
    return render_template('view_order.html', order=order, order_items=order_items)


# In app.py

@app.route('/view_offers')
@login_required
def view_offers():
    # You can add logic here to fetch and display any offers available to the user.
    # For now, we’ll render a template called "view_offers.html".
    return render_template('view_offers.html')


@app.route('/apply_membership_discount', methods=['POST'])
@login_required
def apply_membership_discount():
    membership_id = request.form['membership_id']
    
    # Check if membership ID exists and is associated with the current user
    membership_card = MembershipCard.query.filter_by(member_id=membership_id, user_id=current_user.user_id).first()
    
    if not membership_card:
        flash("Invalid Membership ID or not associated with your account.", "error")
        return redirect(url_for('place_order'))
    if membership_card.expiry_date and membership_card.expiry_date < datetime.now().date():
        flash("Your membership is expired. Please renew it to apply discounts.", "error")
        return redirect(url_for('place_order'))
    # Apply a 10% discount
    cart = session.get('cart', [])
    total_amount = sum(item['quantity'] * item['unit_price'] for item in cart)
    discount = total_amount * 0.10
    
    # Store the discount in the session
    session['membership_discount'] = discount
    flash("Membership discount applied successfully!", "success")
    
    return redirect(url_for('place_order'))

@app.route('/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    if request.method == 'POST':
        online_customer = OnlineCustomer.query.filter_by(user_id=current_user.user_id).first()
        if not online_customer:
            flash("You must be a registered online customer to place an order.", "error")
            return redirect(url_for('dashboard'))
        # Get payment details from form
        payment_method = request.form['payment_method']
        transaction_id = request.form.get('transaction_id') if payment_method == 'online' else None
        cart = session.get('cart', [])
        if not cart:
            flash("Your cart is empty. Add items to place an order.", "error")
            return redirect(url_for('place_order'))
        
        total_amount = sum(item['quantity'] * item['unit_price'] for item in cart)

        # Apply membership discount if available
        discount = session.pop('membership_discount', 0)
        final_amount = total_amount - discount
        for item in cart:
            product = Product.query.get(item['product_id'])
            if not product:
                flash(f"Product with ID {item['product_id']} does not exist.", "error")
                return redirect(url_for('place_order'))
            
            if product.quantity < item['quantity']:
                flash(f"Insufficient stock for product {product.name}. Available: {product.quantity}, Requested: {item['quantity']}.", "error")
                return redirect(url_for('place_order'))

        
        # Create a new Order without payment_method and transaction_id
        order = Order(
            order_num=str(datetime.now().timestamp()),  # Unique order number based on timestamp
            user_id=current_user.user_id,
            order_date=datetime.now(),
            total_amount=final_amount
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID before committing
        
        # Add each cart item to OrderProduct and update product stock
        for item in cart:
            product = Product.query.get(item['product_id'])
            order_product = OrderProduct(
                order_num=order.order_num,
                product_id=product.product_id,
                quantity=item['quantity'],
                unit_price=product.unit_price
            )
            db.session.add(order_product)
            
            # Update product stock
            product.quantity -= item['quantity']


        # Commit all changes
        db.session.commit()
        session.pop('cart', None)  # Clear cart after placing order

        # Display success message based on payment method
        if payment_method == 'online' and transaction_id:
            flash(f'Order placed successfully with transaction ID: {transaction_id}', 'success')
        else:
            flash('Order placed successfully with Cash on Delivery (COD)', 'success')

        return redirect(url_for('view_orders'))

    # Display available products and cart contents
    products = Product.query.all()
    cart = session.get('cart', [])
    total_amount = sum(item['quantity'] * item['unit_price'] for item in cart)
    discount = session.get('membership_discount', 0)
    final_amount = total_amount - discount
    cart_items = [{'product': Product.query.get(item['product_id']), 'quantity': item['quantity']} for item in cart]

    return render_template(
        'place_order.html',
        products=products,
        cart_items=cart_items,
        total_amount=total_amount,
        discount=discount,
        final_amount=final_amount
    )

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    product = Product.query.get(product_id)

    if product:
        cart = session.get('cart', [])

        # Check if product is already in cart
        for item in cart:
            if item['product_id'] == product_id:
                # Update quantity if product already in cart
                item['quantity'] += quantity
                break
        else:
            # Add new product to cart if not already present
            cart.append({'product_id': product.product_id, 'quantity': quantity, 'unit_price': float(product.unit_price)})

        # Update session cart
        session['cart'] = cart
        flash(f'Added {quantity} of {product.name} to cart!', 'success')

    return redirect(url_for('place_order'))

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', [])

    # Filter out the item with the matching product_id
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart  # Update the session cart

    flash('Item removed from cart.', 'success')
    return redirect(url_for('place_order'))


@app.route('/view_orders')
@login_required
def view_orders():
    if hasattr(current_user, 'user_id'):  # Customer
        orders = Order.query.filter_by(user_id=current_user.user_id).all()
    else:  # Employee
        orders = Order.query.all()
    
    return render_template('view_orders.html', orders=orders)



@app.route('/edit_order/<order_num>', methods=['GET', 'POST'])
@login_required
def edit_order(order_num):
    order = Order.query.get(order_num)
    order_items = order.order_products  # Assuming relationship with OrderProduct is established
    all_products = Product.query.all()

    if request.method == 'POST':
        # Update quantities of existing items
        for item in order_items:
            quantity = request.form.get(f'quantity_{item.product_id}')
            if quantity:
                item.quantity = int(quantity)
        
        # Check if a new item is being added
        new_product_id = request.form.get('new_product_id')
        new_quantity = request.form.get('new_quantity')
        
        if new_product_id and new_quantity:
            new_item = OrderProduct(
                order_num=order_num,
                product_id=new_product_id,
                quantity=int(new_quantity),
                unit_price=Product.query.get(new_product_id).unit_price
            )
            db.session.add(new_item)

        # Calculate the new total amount for the order
        order.total_amount = sum(item.quantity * item.unit_price for item in order.order_products)

        db.session.commit()
        return redirect(url_for('view_orders'))

    return render_template('edit_order.html', order_items=order_items, all_products=all_products)




@app.route('/cancel_order/<order_num>', methods=['POST'])
@login_required
def cancel_order(order_num):
    # First, delete associated items in OrderProduct
    OrderProduct.query.filter_by(order_num=order_num).delete()

    # Then, delete the order from Orders
    order = Order.query.get(order_num)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash("Order canceled successfully.", "success")
    else:
        flash("Order not found.", "error")

    return redirect(url_for('view_orders'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/offers')
@login_required
def offers():
    sales = Sale.query.all()  # Fetch all offers from the Sale table
    return render_template('offers.html', sales=sales)



if __name__ == '__main__':
    db.create_all(app=app)  # Ensure app context for create_all
    app.run(debug=True)




@app.route('/view_membership')
@login_required
def view_membership():
    # Add logic to retrieve and display membership details
    return render_template('membership.html')  # Ensure you have membership.html created



from flask import render_template, redirect, url_for, request, flash


@app.route('/view_product/<product_id>')
def view_product(product_id):
    # Logic to view a specific product
    product = Product.query.get_or_404(product_id)
    return render_template('view_product.html', product=product)


@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Fetch form data
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.unit_price = request.form.get('unit_price')
        product.quantity = request.form.get('quantity')
        product.product_type = request.form.get('product_type')
        
        # Commit changes to the database
        db.session.commit()
        return redirect(url_for('search_products'))

    return render_template('edit_product.html', product=product)


@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('search_products'))

# Order Management



@app.route('/store_info')
@login_required
def store_info():
    stores = Store.query.all()
    return render_template('store_info.html', stores=stores)



@app.route('/supplier_info')
def supplier_info():
    suppliers = Supplier.query.options(db.joinedload(Supplier.products)).all()
    return render_template('supplier_info.html', suppliers=suppliers)




@app.route('/delete_customer/<user_id>', methods=['POST'])
def delete_customer(user_id):
    customer = User.query.get(user_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash(f'Customer {user_id} has been deleted.', 'success')
    else:
        flash(f'Customer {user_id} not found.', 'error')
    return redirect(url_for('search_customers'))




@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        name = request.form.get('name')
        description = request.form.get('description')
        unit_price = request.form.get('unit_price')
        quantity = request.form.get('quantity')
        product_type = request.form.get('product_type')

        new_product = Product(
            product_id=product_id,
            name=name,
            description=description,
            unit_price=unit_price,
            quantity=quantity,
            product_type=product_type
        )
        db.session.add(new_product)
        db.session.commit()
        
        return redirect(url_for('search_products'))

    return render_template('add_product.html')



@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplier_id = request.form['supplier_id']
        supplier_name = request.form['supplier_name']
        product_ids = request.form.getlist('product_ids')  # Get multiple selected products

        new_supplier = Supplier(supplier_id=supplier_id, supplier_name=supplier_name)
        new_supplier.products = Product.query.filter(Product.product_id.in_(product_ids)).all()  # Assign products
        db.session.add(new_supplier)
        db.session.commit()
        return redirect(url_for('supplier_info'))

    products = Product.query.all()
    return render_template('add_supplier.html', products=products)


@app.route('/edit_supplier/<supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.supplier_name = request.form['supplier_name']
        product_ids = request.form.getlist('product_ids')

        supplier.products = Product.query.filter(Product.product_id.in_(product_ids)).all()  # Update associated products
        db.session.commit()
        return redirect(url_for('supplier_info'))

    products = Product.query.all()
    return render_template('edit_supplier.html', supplier=supplier, products=products)
