from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import DateTime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    image_url = db.Column(db.String(length=100), nullable=False)
    carts = db.relationship('Cart', backref='item', lazy=True)
    seller = db.Column(db.Integer,  db.ForeignKey('user.id'), nullable=False)
    item = db.relationship("OrderItems", backref='ordered', lazy=True)

    def _repr_(self):
        return f'Item {self.name}'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    name = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    mobile = db.Column(db.Integer(), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    role = db.Column(db.String(length=10), nullable=False)
    carts = db.relationship('Cart', backref='user', lazy=True)
    seller = db.relationship('Item', backref='sold_by', lazy=True)
    seller_apply = db.relationship('SellerApproval', backref='applied', lazy=True)
    ordered = db.relationship('Orders', backref='ordered', lazy = True)
    address = db.relationship('Address', backref='user_address', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Cart(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer(), nullable=False)

class SellerApproval(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False)
    aadhar = db.Column(db.Integer(), nullable=False, unique=True)
    image_path = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

class Orders(db.Model):
    order_id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    order_date = db.Column(DateTime, default=datetime.now)
    total_price = db.Column(db.Float)
    address = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    order = db.relationship("OrderItems", backref="order_item", lazy=True)

class OrderItems(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    line1 = db.Column(db.String(255), nullable=False)
    line2 = db.Column(db.String(255), nullable=False)
    landmark = db.Column(db.String(255))
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    address = db.relationship("Orders", backref="delivery_address", lazy=True)
