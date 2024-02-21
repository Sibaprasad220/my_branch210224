from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT, jwt_required, current_identity


app = Flask(__name__)
app.config['SECRET_KEY'] = '3EgjhgjhvhjEJBJKBKJuyJHVJtgbfbfgnfgnYFYUVYHyyyyYyYyY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)

# User-Role Association Table
user_role_association = db.Table('user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# Role Model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=user_role_association, backref=db.backref('users', lazy='dynamic'))

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

# Create the database tables
db.create_all()

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(({'message': 'Usernot found '}), 404)
    return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)

jwt = JWT(app, authenticate, identity)

# Resource for user registration
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        if 'username' not in data or 'password' not in data or 'email' not in data or 'roles' not in data:
            return jsonify({'error': 'Username, password, email, and roles are required'}), 400

        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])

        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                new_user.roles.append(role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201

# Resource for user login
class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            access_token = jwt.jwt_encode_callback({'identity': user.id})
            return jsonify({'access_token': access_token.decode('utf-8')})
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

# Resource for managing inventory
class InventoryResource(Resource):
    #############CReate inventory #############
    @jwt_required()
    def post(self):
        current_user = current_identity
        data = request.get_json()

        if 'product_name' not in data or 'quantity' not in data:
            return jsonify({'error': 'Both product_name and quantity are required'}), 400

        new_item = InventoryItem(
            product_name=data['product_name'],
            vendor=data.get('vendor', ''),
            mrp=data.get('mrp', 0.0),
            batch_num=data.get('batch_num', ''),
            batch_date=data.get('batch_date', None),
            quantity=data['quantity'],
            user=current_user
        )

        # Check if the user has the 'Store Manager' role for auto-approval
        if 'Store Manager' in [role.name for role in current_user.roles]:
            new_item.status = 'Approved'

        db.session.add(new_item)
        db.session.commit()

        return jsonify({'message': 'Inventory item added successfully'}), 201
    
############### Fetch inventory details
    @jwt_required()
    def get(self):
        items = InventoryItem.query.all()
        inventory_list = [{'id': item.id, 'product_name': item.product_name, 'vendor': item.vendor,
                            'mrp': item.mrp, 'batch_num': item.batch_num, 'batch_date': str(item.batch_date),
                            'quantity': item.quantity, 'status': item.status, 'user_id': item.user_id} for item in items]
        return jsonify({'inventory': inventory_list})



# Resource for approving inventory records
class ApproveInventoryResource(Resource):
    #################Approve inventory records################
    @jwt_required()
    def get(self):
        current_user = current_identity

        # Check if the user has the 'Store Manager' role
        if 'Store Manager' not in [role.name for role in current_user.roles]:
            return jsonify({'error': 'Access denied. Only Store Managers can approve inventory items'}), 403

        pending_items = InventoryItem.query.filter_by(status='Pending').all()
        pending_list = [{'id': item.id, 'product_name': item.product_name, 'quantity': item.quantity} for item in pending_items]

        return jsonify({'pending_inventory': pending_list})

    @jwt_required()
    def put(self, item_id):
        current_user = current_identity
        item = InventoryItem.query.get(item_id)

        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404

        # Check if the user has the 'Store Manager' role
        if 'Store Manager' not in [role.name for role in current_user.roles]:
            return jsonify({'error': 'Access denied. Only Store Managers can approve inventory items'}), 403

        item.status = 'Approved'
        db.session.commit()

        return jsonify({'message': f'Inventory item with ID {item_id} approved successfully'}), 200

api.add_resource(RegisterResource, '/register')
api.add_resource(LoginResource, '/login')
api.add_resource(InventoryResource, '/inventory')
api.add_resource(ApproveInventoryResource, '/inventory/approve', '/inventory/approve/<int:item_id>')

if __name__ == '__main__':
    app.run(debug=True)