from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import HiddenField

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('ItemOwner', back_populates='owner')

    @property
    def prettier_budget(self):
        rounded_budget = round(self.budget, 2)
        formatted_budget = f"{rounded_budget:,.2f}"

        return formatted_budget + " PLN"


    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        ownership_record = ItemOwner.query.filter_by(item_id=item_obj.id, owner_id=self.id).first()
        return ownership_record is not None

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Float(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owners = db.relationship('ItemOwner', back_populates='item')
    change_percent = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user):
        ownership_record = ItemOwner.query.filter_by(item_id=self.id, owner_id=user.id).first()
        if ownership_record:
            ownership_record.quantity += 1
        else:
            ownership_record = ItemOwner(item_id=self.id, owner_id=user.id, quantity=1)
            db.session.add(ownership_record)
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        ownership_record = ItemOwner.query.filter_by(item_id=self.id, owner_id=user.id).first()
        if ownership_record:
            if ownership_record.quantity > 1:
                ownership_record.quantity -= 1
            else:
                db.session.delete(ownership_record)
            user.budget += self.price
            db.session.commit()

class ItemOwner(db.Model):
    __tablename__ = 'item_owner'
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship("Item", back_populates="owners")
    owner = db.relationship("User", back_populates="items")
