from app.models import db

# Inventory Item Model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100))
    mrp = db.Column(db.Float)
    batch_num = db.Column(db.String(50))
    batch_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Approved/Pending
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('inventory_items', lazy='dynamic'))