from flask import Flask, request
import json
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({'error': message}), code

def create_tables():
    DB.create_all()

@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
"""
Returns every user (i.e., every item in users table) and success code 200.
"""
@app.route("/api/users/")
def get_all_users():
    return success_response(DB.query_all_users())

"""
Creates a user with name, username, and balance specified in body. If name and/or username are empty, then returns 400 status code, 
else a 201 success code along with new user's full information
"""
@app.route("/api/users/", methods = ["POST"])
def create_user():
    body = json.loads(request.data) 
    username = body["username"]
    if username is None:
        return failure_response("No username provided!", 400)
    name = body["name"]
    if name is None:
        return failure_response("No name provided!", 400)
    #if this far -- then both are provided
    balance = body["balance"]
    users_id = DB.insert_user_table(name, username, balance)
    user = DB.query_user_by_id(users_id)
    if user is None:
        return failure_response("Something went wrong while creating task!", 500)
    return success_response(user, 201)

"""
Returns a user of specified id from url. 404 status code if user not found, else 200 status code.
"""
@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.query_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")
    return success_response(user)

"""
Deletes user of specified id, 404 status code if user not found, else 200 status code
"""
@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.query_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")
    DB.remove_user(user_id)
    return success_response(user)


"""
Sends amount between two users, with ids and amount specified in body. Nonexistent or invalid IDs return a 400 status code
and an insufficient sender balance also returns a 400 status code, else a 200 success code.
"""
@app.route("/api/send/", methods = ["POST"])
def send_money():
    body = json.loads(request.data) 
    sender_id = body["sender_id"]
    if (sender_id is None) or (DB.query_user_by_id(sender_id) is None):
        return failure_response("No sender ID provided or invalid ID!", 400)
    receiver_id = body["receiver_id"]
    if (receiver_id is None) or (DB.query_user_by_id(receiver_id) is None):
        return failure_response("No receiver ID provided or invalid ID!", 400)
    amount = body["amount"] #amount being transferred
    sender_balance = DB.query_user_balance(sender_id)
    if sender_balance < amount: #can't transfer
        return failure_response("Insufficient funds!", 400)
    #Now, update the sender and receiver's balances separately
    DB.update_user(sender_id, -amount) #deducted from sender
    DB.update_user(receiver_id, amount) #added to receiver
    return success_response(body)

"""
Resets tables to empty value for graders' postman evaluation.
"""
@app.route("/api/reset/", methods=["POST"])
def reset_tables():
    DB.reset_tables()  # Call the reset_tables() method from your DatabaseDriver class
    return "Tables reset successfully", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
