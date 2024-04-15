from market import app, db, login_manager
from flask import render_template, redirect, url_for, flash, request, jsonify
from market.models import Item, User, ItemOwner
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    # Fetch owned items with correct reference to ItemOwner
    owned_items = db.session.query(
        Item.id, Item.name, Item.price, ItemOwner.quantity
    ).join(ItemOwner, ItemOwner.item_id == Item.id).filter(
        ItemOwner.owner_id == current_user.id
    ).all()

    items = Item.query.all()  # Fetch all items available in the market

    if request.method == "POST":
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')

        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

        return redirect(url_for('market_page'))

    return render_template('market.html', items=items, owned_items=owned_items, purchase_form=purchase_form, selling_form=selling_form)

def market_page_logfirst():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login_page'))
    return redirect(url_for('main.market_page'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/api/prices')
def get_prices():
    all_items = Item.query.all()
    items_data = [{'id': item.id, 'price': item.price, 'change_percent': item.change_percent} for item in all_items]
    return jsonify(items_data)

@app.route('/sell-item/<int:item_id>', methods=['POST'])
def sell_item(item_id):
    owned_item = db.session.query(ItemOwner).options(joinedload(ItemOwner.item)).filter_by(
        item_id=item_id, owner_id=current_user.id
    ).first()

    if owned_item and owned_item.quantity > 0:
        if owned_item.quantity > 1:
            owned_item.quantity -= 1
        else:
            db.session.delete(owned_item)
        current_user.budget += owned_item.item.price
        db.session.commit()
        flash(f"Successfully sold {owned_item.item.name}.", "success")
    else:
        flash("No such item to sell or zero quantity!", "error")

    return redirect(url_for('market_page'))