# app/resources/approve_inventory_resource.py
from flask import jsonify
from flask_jwt import jwt_required, current_identity
from flask_restful import Resource
from app.models import db, InventoryItem


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