from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User, SellerApproval, Cart, Orders, OrderItems, Address
from market.forms import RegisterForm, LoginForm, SellerForm, ItemForm, AddressForm
from market import db
from flask_login import login_user, logout_user
from werkzeug.utils import secure_filename
import sys
import os
from datetime import datetime

app.config['UPLOAD_FOLDER_PROFILES'] = 'market/static/profile'
app.config['UPLOAD_FOLDER_PRODUCTS'] = 'market/static/products'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


@app.route("/")
@app.route("/market")
def market_page():
    items = Item.query.all()
    return render_template('market.html', item_name=items)

@app.route("/register", methods = ['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username = form.username.data,
                              name = form.name.data,
                              email_address = form.email_address.data,
                              mobile = form.mobile.data,
                              password = form.password1.data,
                              role = 'Customer')
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username = form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password = form.password.data):
            login_user(attempted_user)
            flash(f'Succesfully logged in as {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Incorrect username or password', category='danger')
    return render_template('login.html', form = form)

@app.route("/logout")
def logout_page():
    logout_user()
    flash('You have logged out', category='info')
    return redirect(url_for('login_page'))

@app.route("/profile")
def profile_page():
    return render_template('profile.html')

@app.route("/product/<int:product_id>", methods =  ['GET'])
def product_page(product_id):
    product = Item.query.get(product_id)
    seller = User.query.get(product.seller)
    return render_template('product_page.html', product=product, seller=seller)

@app.route('/add_to_cart/<int:user_id>/<int:product_id>/<int:quantity>')
def add_to_cart(user_id, product_id, quantity):
    check = Cart.query.filter_by(user_id = user_id,
                                 item_id = product_id).first()
    if check == None:
        cart = Cart(user_id = user_id,
                item_id = product_id,
                quantity = quantity)
        db.session.add(cart)
        db.session.commit()
        flash('Added to cart', category='success')
        return redirect(url_for('product_page', product_id = product_id))
    check.quantity += quantity
    db.session.commit()
    flash('Cart updated', category='success')
    return redirect(url_for('product_page', product_id = product_id))

@app.route("/cart/<int:user_id>")
def cart_page(user_id):
    cart_items = db.session.query(Cart, Item).filter_by(user_id = user_id).join(Item, Cart.item_id == Item.id).all()
    total_cost = sum(cart.quantity * item.price for cart, item in cart_items)
    return render_template('cart.html', cart_items = cart_items, total_cost = total_cost)

@app.route('/cart/remove/<int:user_id>/<int:item_id>')
def remove_from_cart(user_id, item_id):
    Cart.query.filter_by(user_id = user_id, item_id = item_id).delete()
    db.session.commit()
    flash('Removed from cart', category='info')
    return redirect(url_for('cart_page', user_id = user_id))

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    Item.query.filter_by(id = item_id).delete()
    db.session.commit()
    flash('Item removed from market', category = 'info')
    return redirect(url_for('market_page'))

@app.route('/select_address/<int:user_id>')
def select_address(user_id):
    address_list = Address.query.filter_by(user_id = user_id).all()
    return render_template('select_address.html', address_list = address_list)

@app.route('/checkout/<int:user_id>/<int:address_id>', methods=['POST', 'GET'])
def checkout(user_id, address_id):
    cart_items = db.session.query(Cart, Item).filter_by(user_id = user_id).join(Item, Cart.item_id == Item.id).all()
    total_cost = sum(cart.quantity * item.price for cart, item in cart_items)

    order = Orders(user_id = cart_items[0][0].user_id,
                   total_price = total_cost,
                   address = address_id)
    db.session.add(order)
    db.session.commit()
    order = Orders.query.order_by(Orders.order_id.desc()).first()
    for cart_item in cart_items:
        data = cart_item[0]
        order_item = OrderItems(order_id = order.order_id,
                                item_id = int(data.item_id),
                                quantity = int(data.quantity))
        db.session.add(order_item)
        Cart.query.filter_by(user_id = user_id, item_id = data.item_id).delete()
    db.session.commit()
    flash('Successfully checked out', category='success')
    return redirect(url_for('market_page'))

@app.route('/checkout/<status>')
def checkout_status(status):
    if status == 'success':
        flash('Successfully checkout out', 'success')
        return redirect(url_for('market_page'))
    else:
        flash('Checkout failed', 'fail')
        return redirect(url_for('cart_page'))

@app.route("/seller_application/<int:user_id>", methods = ['GET', 'POST'])
def seller_apply(user_id):
    user = User.query.filter_by(id = user_id).first()
    print(user, file=sys.stderr)
    form = SellerForm()
    if form.validate_on_submit():
        application = SellerApproval.query.filter_by(user_id = user_id).first()
        if application != None:
            print(application, file=sys.stderr)
            flash('You have already applied before', category='danger')
            return redirect(url_for('market_page'))
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER_PROFILES'], filename))

        seller_approval = SellerApproval(name = user.name,
                                          aadhar = form.aadhar.data,
                                          image_path = f'{filename}',
                                          user_id = user_id)
        db.session.add(seller_approval)
        db.session.commit()
        flash('Successfully applied for seller', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error applying: {err_msg}', category='danger')
    return render_template('seller_apply.html', form = form, user = user)

@app.route('/view_applications')
def view_applications():
    applications = SellerApproval.query.all()
    return render_template('view_applications.html', applications = applications)

@app.route('/application/<int:seller_id>')
def application_page(seller_id):
    seller = SellerApproval.query.get(seller_id)
    return render_template('application_page.html', seller = seller)

@app.route('/application/<status>/<int:seller_id>')
def approve_seller(status, seller_id):
    if status == 'approve':
        seller = SellerApproval.query.filter_by(id = seller_id).first()
        user = User.query.filter_by(id = seller.user_id).first()
        user.role = 'Seller'
        SellerApproval.query.filter_by(id = seller_id).delete()
        db.session.commit()
        return redirect(url_for('view_applications'))
    else:
        SellerApproval.query.filter_by(id = seller_id).delete()
        db.session.commit()
        return redirect(url_for('view_applications'))

@app.route('/add_item/<int:seller_id>', methods = ['GET', 'POST'])
def add_item(seller_id):
    form = ItemForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], filename))

        new_item = Item(name = form.name.data,
                        price = form.price.data,
                        description = form.description.data,
                        image_url = f'{filename}',
                        seller = seller_id)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully', category='success')
        return redirect(url_for('market_page'))
    return render_template('add_item.html', form = form)

@app.route('/not_logged_in')
def not_logged_in():
    flash('Please log in to add items to cart', category='info')
    return redirect(url_for('login_page'))

@app.route('/orders/<int:user_id>')
def display_orders(user_id):
    orders = db.session.query(Orders).filter_by(user_id=user_id).all()
    order_items = []
    for order in orders:
        original_datetime = datetime.strptime(str(order.order_date), "%Y-%m-%d %H:%M:%S.%f")
        print(original_datetime.strftime("%d-%m-%Y"), file=sys.stderr)
        order_details = {
            'order_id': order.order_id,
            'order_date': original_datetime.strftime("%d-%m-%Y"),
            'total_price': order.total_price,
            'items': []
        }
        items = db.session.query(OrderItems, Item).\
            filter(OrderItems.order_id == order.order_id).\
            filter(OrderItems.item_id == Item.id).all()
        for order_item, item in items:
            order_item_info = {
                'name': item.name,
                'quantity': order_item.quantity,
                'image_url': item.image_url,
                'item_price': item.price
            }
            order_details['items'].append(order_item_info)
        
        order_items.append(order_details)
    return render_template('display_orders.html', order_items=order_items)

@app.route('/addresses/<int:user_id>')
def addresses(user_id):
    address_list = Address.query.filter_by(user_id = user_id).all()
    print(address_list, file=sys.stderr)
    return render_template('address.html', address_list = address_list)

@app.route('/add_address/<int:user_id>', methods = ['GET', 'POST'])
def add_address(user_id):
    form = AddressForm()
    if form.validate_on_submit():
        address = Address(user_id = user_id,
                      line1 = form.line1.data,
                      line2 = form.line2.data,
                      landmark = form.landmark.data,
                      city = form.city.data,
                      state = form.state.data,
                      country = form.country.data,
                      pincode = form.pincode.data)
        db.session.add(address)
        db.session.commit()
        flash('Address added successfully', category = 'success')
        return redirect(url_for('addresses', user_id = user_id))
    return render_template('add_address.html', form = form)

@app.route('/delete_address/<int:user_id>/<int:address_id>')
def delete_address(user_id, address_id):
    Address.query.filter_by(id = address_id).delete()
    db.session.commit()
    flash('Address deleted', category='info')
    return redirect(url_for('addresses', user_id = user_id))

@app.route("/search_results/", methods=['GET'])
def search_results():
    query = request.args.get('query')
    product = Item.query.filter(Item.name.ilike(f"%{query}%")).all()
    if product:
        return render_template('market.html', item_name=product)
    else:
        flash('Product not found!', category='info')
        return redirect(url_for('market_page'))
    
