from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    terms = db.Column(db.Boolean, unique=False, default=False)
    cart = db.relationship('Cart', uselist=False, back_populates='user')

class Product(db.Model):
    __bind_key__ = 'store'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Product {self.name}>"
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user = db.relationship('User', back_populates='cart')

    def __repr__(self):
        return f"<Cart {self.id} for User {self.user_id}>"


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False) 
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cart = db.relationship('Cart', back_populates='items')

    def get_product(self):
        from .models import Product 
        return db.session.execute(
            db.select(Product).filter_by(id=self.product_id).execution_options(bind_key="store")
        ).scalar()

    def __repr__(self):
        return f"<CartItem {self.quantity} of Product {self.product_id} in Cart {self.cart_id}>"