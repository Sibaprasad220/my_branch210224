# app/routes/routes.py
from flask import Blueprint
from app.resources.register_resource import RegisterResource
from app.resources.login_resource import LoginResource
from app.resources.inventory_resource import InventoryResource, ApproveInventoryResource

routes = Blueprint('routes', __name__)

from app import create_app  # Import create_app after routes blueprint is defined

api = create_app().api  # Access the Flask-RESTful Api instance from create_app()

api.add_resource(RegisterResource, '/register')
api.add_resource(LoginResource, '/login')
api.add_resource(InventoryResource, '/inventory')
api.add_resource(ApproveInventoryResource, '/inventory/approve', '/inventory/approve/<int:item_id>')
