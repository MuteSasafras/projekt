from flask_apscheduler import APScheduler
from market.models import db, Item
import random

scheduler = APScheduler()

def adjust_prices():
    with scheduler.app.app_context():
        all_items = Item.query.all()
        for item in all_items:
            change_percent = random.uniform(-0.15, 0.15)
            new_price = item.price * (1 + change_percent)
            item.price = round(new_price, 2)
            item.change_percent = round(change_percent * 100, 2)
        db.session.commit()

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.task('interval', id='adjust_prices_task', seconds=10)
    def scheduled_price_adjustment():
        adjust_prices()