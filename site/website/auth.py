from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Product, Cart, CartItem
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Bem vindo!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Senha inserida incorreta.', category='error')
        else:
            flash('Email não cadastrado.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        terms = request.form.get('terms')  # This should match the HTML name attribute

        # Check if the terms checkbox is not checked
        if not terms:
            flash('Você deve aceitar os termos e condições para criar a conta.', category='error')
        elif User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', category='error')
        elif len(email) < 4:
            flash('Email inválido.', category='error')
        elif len(first_name) < 2:
            flash('Seu nome deve ter mais de 1 caractere.', category='error')
        elif password1 != password2:
            flash('As senhas não são iguais.', category='error')
        elif len(password1) < 7:
            flash('A senha deve ter pelo menos 7 caracteres.', category='error')
        else:
            # Create new user
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            # Log in the user immediately after sign-up
            login_user(new_user, remember=True)
            flash('Conta criada com sucesso!', category='success')
            return redirect(url_for('views.home'))  # Redirect to home page

    return render_template("sign_up.html", user=current_user)


@auth.route('/store')
def store():
    products = Product.query.all()
    return render_template('store.html', products=products, user=current_user)

@auth.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_page.html', product=product, user=current_user)

@auth.route('/contact')
def contact():
    return render_template('contact.html', user=current_user)

@auth.route('/about')
def about():
    return render_template('about.html', user=current_user)

@auth.route('/cart')
@login_required
def view_cart():
    cart = current_user.cart
    items = cart.items if cart else []
    total_price = sum(item.get_product().price * item.quantity for item in items)
    return render_template('cart.html', cart=cart, items=items, total_price=total_price, user=current_user)

@auth.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.execution_options(bind_key='store').get(product_id)
    if not product:
        flash('Produto não encontrado.', category='error')
        return redirect(url_for('auth.store'))

    if not current_user.cart:
        new_cart = Cart(user_id=current_user.id)
        db.session.add(new_cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=current_user.cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart_id=current_user.cart.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'Adicionou {product.name} ao seu carrinho!', category='success')
    return redirect(url_for('auth.store'))

@auth.route('/remove-from-cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item or cart_item.cart.user_id != current_user.id:
        flash('Item não encontrado no carrinho.', category='error')
        return redirect(url_for('auth.view_cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removido do carrinho.', category='success')
    return redirect(url_for('auth.view_cart'))

@auth.route('/empty-cart', methods=['POST'])
@login_required
def empty_cart():
    cart = current_user.cart
    if cart:
        cart.items.clear()
        db.session.commit()
        flash('Compra finalizada com sucesso!', category='success')
    else:
        flash('Seu carrinho está vazio.', category='error')

    return redirect(url_for('auth.view_cart'))
    

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth.route('/change_first_name', methods=['POST'])
def change_first_name():
    if request.method == 'POST':
        new_first_name = request.form['newFirstName']
        current_user.first_name = new_first_name
        db.session.commit()
        return redirect(url_for('auth.profile'))

@auth.route('/change_email', methods=['POST'])
def change_email():
    if request.method == 'POST':
        new_email = request.form['newEmail']
        current_user.email = new_email
        db.session.commit()
        return redirect(url_for('auth.profile'))

@auth.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']
        
        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('auth.profile'))
        
        if len(new_password) < 7:
            flash('Senha tem que ter pelo menos 7 caracteres.', category='error')
            return redirect(url_for('auth.profile'))

        if check_password_hash(current_user.password, current_password):
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Senha mudada com sucesso!", "success")
            return redirect(url_for('auth.profile'))
        else:
            flash("Senha atual incorreta", "error")
            return redirect(url_for('auth.profile'))