import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)
conn = psycopg2.connect("dbname='usermgt' user='aidenthomas' host='localhost'")
cursor = conn.cursor()

cursor.execute(
  '''
  CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    phone VARCHAR,
    city VARCHAR,
    state VARCHAR,
    active BOOLEAN NOT NULL DEFAULT True,
    org_id INT
  );
  '''
)
conn.commit()

cursor.execute(
  '''
  CREATE TABLE IF NOT EXISTS organizations (
    org_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone VARCHAR,
    city VARCHAR,
    state VARCHAR,
    active BOOLEAN NOT NULL DEFAULT True,
    type VARCHAR
  )
  '''
)
conn.commit()

def get_user_from_list(user_fields):
  return {
    'user_id':user_fields[0],
    'first_name':user_fields[1],
    'last_name':user_fields[2],
    'email':user_fields[3],
    'phone':user_fields[4],
    'city':user_fields[5],
    'state':user_fields[6],
    'organization':{
      'org_id':user_fields[9],
      'name':user_fields[10],
      'phone':user_fields[11],
      'city':user_fields[12],
      'state':user_fields[13],
      'active':user_fields[14],
      'type':user_fields[15]
    },
    'active':user_fields[8]
  }

def get_org_from_list(org_fields):
  return {
    'org_id':org_fields[0],
    'name':org_fields[1],
    'phone':org_fields[2],
    'city':org_fields[3],
    'state':org_fields[4],
    'active':org_fields[5],
    'type':org_fields[6]
  }

@app.route('/orgs/add', methods=['POST'])
def add_organization():
  data = request.json

  name = data.get('name')
  phone = data.get('phone')
  if len(phone) > 10:
    return "The length of phone number cannot be more than 10", 400
  city = data.get('city')
  state = data.get('state')
  active = True
  if 'active' in data:
    active = (data.get('active') != 'false')
  type = data.get('type')
  
  cursor.execute(
  '''
  INSERT INTO organizations (name, phone, city, state, active, type) VALUES (%s, %s, %s, %s, %s, %s)
  ''', (name, phone, city, state, active, type)
  )
  conn.commit()

  return "Organization added successfully", 200

@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
  cursor.execute(
    """
      SELECT * FROM organizations WHERE active='t';
    """)
  results = cursor.fetchall()
  
  if results:
    orgs = []
    for o in results:
      org_record = get_org_from_list(o)

      orgs.append(org_record)
    return jsonify(orgs), 200
  else:
    return 'No organizations found', 404

  return jsonify(results), 200

@app.route('/orgs/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
  if not org_id.isnumeric():
    return f"Invalid user id: {org_id}", 400
  cursor.execute(
    "SELECT * FROM organizations WHERE org_id=%s;", (org_id, ))
  org = cursor.fetchone()

  if not org:
    return 'Organization not found', 404
  else:
    org_record = get_org_from_list(org)
    
  return jsonify(org_record), 200

@app.route('/orgs/deactivate/<org_id>', methods=['PUT'])
def deactivate_org_by_id(org_id):
  if not org_id.isnumeric():
    return f"Invalid organization id: {org_id}", 400
  cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
  result = cursor.fetchone()

  if not result:
    return 'Organization not found', 404
  else:
    cursor.execute("UPDATE organizations SET active='f' WHERE org_id=%s", (org_id,))
    conn.commit()

  return "Organization deactivated successfully", 200

@app.route('/orgs/activate/<org_id>', methods=['PUT'])
def activate_org_by_id(org_id):
  if not org_id.isnumeric():
    return f"Invalid organization id: {org_id}", 400
  cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
  result = cursor.fetchone()

  if not result:
    return 'Organization not found', 404
  else:
    cursor.execute("UPDATE organizations SET active='t' WHERE org_id=%s", (org_id,))
    conn.commit()

  return "Organization activated successfully", 200

@app.route('/orgs/delete/<org_id>', methods=['DELETE'])
def delete_organization(org_id):
  if not org_id.isnumeric():
    return f"Invalid user id: {org_id}", 400
  cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
  result = cursor.fetchone()

  if not result:
    return "Organization not found", 404
  else:
    cursor.execute("DELETE FROM organizations WHERE org_id=%s", (org_id,))
    conn.commit()
  
  return "Organization deleted successfully", 200

@app.route('/orgs/update/<org_id>', methods=['PUT'])
def update_org_info(org_id):
  data = request.json
  if not org_id.isnumeric():
    return f"Invalid organization id: {org_id}", 400
  cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
  result = cursor.fetchone()

  if not result:
    return "Organization not found", 404
  else:
    print(result)
    org = {
      'name':result[1],
      'phone':result[2],
      'city':result[3],
      'state':result[4],
      'type':result[6]
    }

    for d in data:
      org[d] = data[d]

    name = org['name']
    if not name:
      return "Organization name cannot be null", 400
    phone = org['phone']
    if len(phone) > 10:
      return "The length of phone number cannot be more than 10", 400
    city = org['city']
    state = org['state']
    type = org['type']
    cursor.execute(f"UPDATE organizations SET name=%s, phone=%s, city=%s, state=%s, type=%s WHERE org_id=%s", (name, phone, city, state, type, org_id))
    conn.commit()
    
  return jsonify(org), 200

@app.route('/users/add', methods=['POST'])
def add_user():
  data = request.json

  first_name = data.get('first_name')
  last_name = data.get('last_name')
  email = data.get('email')
  if not email:
    return "Email must be a non-empty string", 400
  phone = data.get('phone')
  if len(phone) > 10:
    return "The length of phone number cannot be more than 10", 400
  city = data.get('city')
  state = data.get('state')
  org_id = data.get('org_id')

  cursor.execute(
  '''
  INSERT INTO users (first_name, last_name, email, phone, city, state, org_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
  ''', (first_name, last_name, email, phone, city, state, org_id)
  )
  conn.commit()

  return 'User Added', 201

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
  cursor.execute(
  """
  SELECT 
    u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active,
    o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
  FROM users u
    LEFT OUTER JOIN organizations o
      ON u.org_id = o.org_id
    WHERE u.active='t';
  """)
  results = cursor.fetchall()
  
  if results:
    users = []
    for u in results:
      user_record = get_user_from_list(u)

      users.append(user_record)
    return jsonify(users), 200
  else:
    return 'No users found', 404

  return jsonify(results), 200

@app.route('/users/deactivate/<user_id>', methods=['PUT'])
def deactivate_user_by_id(user_id):
  if not user_id.isnumeric():
    return f"Invalid user id: {user_id}", 400
  cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
  result = cursor.fetchone()

  if not result:
    return 'User not found', 404
  else:
    cursor.execute("UPDATE users SET active='f' WHERE user_id=%s", (user_id,))
    conn.commit()

  return "User deactivated successfully", 200

@app.route('/users/activate/<user_id>', methods=['PUT'])
def activate_user_by_id(user_id):
  if not user_id.isnumeric():
    return f"Invalid user id: {user_id}", 400
  cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
  result = cursor.fetchone()

  if not result:
    return 'User not found', 404
  else:
    cursor.execute("UPDATE users SET active='t' WHERE user_id=%s", (user_id,))
    conn.commit()

  return "User activated successfully", 200

@app.route('/users/get-by-id/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
  if not user_id.isnumeric():
    return f"Invalid user id: {user_id}", 400
  cursor.execute(
  '''
  SELECT 
      u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active,
      o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
  FROM users u
      LEFT OUTER JOIN organizations o
          ON u.org_id = o.org_id
  WHERE user_id=%s;
  ''', (user_id,))
  user = cursor.fetchone()

  if not user:
    return 'User not found', 404
  else:
    user_record = get_user_from_list(user)
    
  return jsonify(user_record), 200

@app.route('/users/delete/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
  if not user_id.isnumeric():
    return f"Invalid user id: {user_id}", 400
  cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
  result = cursor.fetchone()

  if not result:
    return "User not found", 404
  else:
    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    conn.commit()
  
  return "User deleted successfully", 200

@app.route('/users/update/<user_id>', methods=['PUT'])
def update_user_info(user_id):
  data = request.json
  if not user_id.isnumeric():
    return f"Invalid user id: {user_id}", 400
  cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
  result = cursor.fetchone()

  if not result:
    return "User not found", 404
  else:
    user = {
      'first_name':result[1],
      'last_name':result[2],
      'email':result[3],
      'phone':result[4],
      'city':result[5],
      'state':result[6]
    }

    for d in data:
      user[d] = data[d]

    first_name = user['first_name']
    last_name = user['last_name']
    email = user['email']
    if not email:
      return "Email must be a non-empty string", 400
    phone = user['phone']
    if len(phone) > 10:
      return "The length of phone number cannot be more than 10", 400
    city = user['city']
    state = user['state']
    cursor.execute(f"UPDATE users SET first_name=%s, last_name=%s, email=%s, phone=%s, city=%s, state=%s WHERE user_id=%s", (first_name, last_name, email, phone, city, state, user_id))
    conn.commit()
    
  return jsonify(user), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='8086')