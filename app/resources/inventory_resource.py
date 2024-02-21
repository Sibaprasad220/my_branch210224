from flask import jsonify, request
from flask_jwt import jwt_required, current_identity
from flask_restful import Resource
from app.models import db, InventoryItem


##########Resource for managing inventory
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