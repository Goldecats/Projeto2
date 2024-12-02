from flask import Blueprint, render_template
from flask_login import current_user
from . import db
from .models import Product

views = Blueprint('views', __name__)


@views.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products, user=current_user)
