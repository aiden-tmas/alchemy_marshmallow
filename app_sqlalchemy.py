from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from db import db, init_db
import uuid

from models.users import Users, user_schema, users_schema
from models.organizations import Organizations, org_schema, orgs_schema

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "usermgt4"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

def create_all():
  with app.app_context():
    db.create_all()

def is_valid_uuid(value):
  try:
    uuid.UUID(str(value))

    return True
  except ValueError:
    return False

#---------------------------------
# ORGANIZATION ROUTES
#---------------------------------

@app.route('/orgs', methods=['GET'])
def get_all_active_orgs():
  org_records = db.session.query(Organizations).filter(Organizations.active==True).all()
  
  if org_records:
    return jsonify(orgs_schema.dump(org_records)), 200

  return 'No organizations found', 404


@app.route('/orgs/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return f'Organization {org_id} not found', 404

  return jsonify(org_schema.dump(org_record)), 200


@app.route('/orgs/add', methods=['POST'])
def add_org():
  request_data = request.json

  name = request_data.get('name')
  if not name:
    return "Organization must have a name", 400
  phone = request_data.get('phone')
  if len(phone) > 10:
    return "The length of phone number cannot be more than 10", 400
  city = request_data.get('city')
  state = request_data.get('state')
  type = request_data.get('type')

  new_org_record = Organizations(name, phone, city, state, type)
  db.session.add(new_org_record)
  db.session.commit()

  return jsonify(org_schema.dump(new_org_record)), 200


@app.route('/orgs/update/<org_id>', methods=['PUT', 'POST', 'PATCH'])
def update_org(org_id):
  request_params = request.json

  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return f'Organization {org_id} not found', 404

  if 'name' in request_params:
    org_record.name = request_params.get('name')
  if 'phone' in request_params:
    org_record.phone = request_params.get('phone')
  if 'city' in request_params:
    org_record.city = request_params.get('city')
  if 'state' in request_params:
    org_record.state = request_params.get('state')
  if 'type' in request_params:
    org_record.type = request_params.get('type')

  db.session.commit()

  return jsonify(org_schema.dump(org_record)), 200


@app.route('/orgs/delete/<org_id>', methods=['DELETE'])
def delete_org(org_id):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return f'Organization {org_id} not found', 404

  db.session.delete(org_record)
  db.session.commit()

  return jsonify(org_schema.dump(org_record)), 200


@app.route('/orgs/activate/<org_id>', methods=['PUT'])
def activate_org(org_id):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return f'Organization {org_id} not found', 404

  org_record.active = True
  db.session.commit()

  return jsonify(org_schema.dump(org_record)), 200


@app.route('/orgs/deactivate/<org_id>', methods=['PUT'])
def deactivate_org(org_id):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return f'Organization {org_id} not found', 404

  org_record.active = False
  db.session.commit()

  return jsonify('Organization deleted'), 200

#---------------------------------
# USER ROUTES
#---------------------------------

@app.route('/users', methods=['GET'])
def get_all_active_users():
  user_records = db.session.query(Users).filter(Users.active==True).all()
  
  if user_records:
    return jsonify(users_schema.dump(user_records)), 200

  return 'No users found', 404


@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
  if not is_valid_uuid(user_id):
    return f"Invalid user_id", 400
  
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return 'User not found', 404
    
  return jsonify(user_schema.dump(user_record)), 200


@app.route('/users/add', methods=['POST'])
def add_user():
  data = request.json

  first_name = data.get('first_name')
  last_name = data.get('last_name')
  email = data.get('email')
  if not email:
    return "User must have an email", 400
  phone = data.get('phone')
  if len(phone) > 10:
    return "The length of phone number cannot be more than 10", 400
  city = data.get('city')
  state = data.get('state')
  org_id = data.get('org_id')

  new_user_record = Users(first_name, last_name, email, phone, city, state, org_id)
  db.session.add(new_user_record)
  db.session.commit()

  return jsonify(user_schema.dump(new_user_record)), 200


@app.route('/users/update/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def update_user(user_id):
  request_params = request.json

  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return jsonify(f'User {user_id} not found'), 404

  if 'first_name' in request_params:
    user_record.first_name = request_params['first_name']
  if 'last_name' in request_params:
    user_record.last_name = request_params['last_name']
  if 'email' in request_params:
    user_record.email = request_params['email']
  if 'phone' in request_params:
    user_record.phone = request_params['phone']
  if 'city' in request_params:
    user_record.city = request_params['city']
  if 'state' in request_params:
    user_record.state = request_params['state']
  if 'org_id' in request_params:
    user_record.org_id = request_params['org_id']
  if 'active' in request_params:
    user_record.active = request_params['active']
  
  db.session.commit()
    
  return jsonify(user_schema.dump(user_record)), 200


@app.route('/users/deactivate/<user_id>', methods=['PUT'])
def deactivate_user_by_id(user_id):
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return 'User not found', 404
  
  user_record.active = False
  db.session.commit()

  return jsonify(user_schema.dump(user_record)), 200


@app.route('/users/activate/<user_id>', methods=['PUT'])
def activate_user_by_id(user_id):
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return 'User not found', 404
  
  user_record.active = True
  db.session.commit()

  return jsonify(user_schema.dump(user_record)), 200


@app.route('/users/delete/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return f"User {user_id} not found", 404

  db.session.delete(user_record)
  db.session.commit()
  
  return 'User deleted', 200


if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port='8086')