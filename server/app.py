from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import asc

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Message CRUD API</h1>'

@app.route('/messages', methods = ['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.order_by(asc(Message.created_at)).all()]
        return make_response(jsonify(messages), 200)
    
    elif request.method == 'POST':
        new_message = Message(
            body = request.form.get("body"),
            username = request.form.get("username"),
        )
        db.session.add(new_message)
        db.session.commit()
        
        message_dict = new_message.to_dict()
        return make_response(message_dict, 201)
        

@app.route('/messages/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
        message = Message.query.filter(Message.id == id).first()
        
        if message == None:
            response_body = {
                "message": "This record does not exist in our database. please try again."
            }
            return make_response(response_body, 404 )
        else:
            if request.method == 'GET':
                message_serialized = message.to_dict()
                return make_response( message_serialized, 200 )

            elif request.method == 'PATCH':
                for attr in request.form:
                    setattr(message, attr, request.form.get(attr))
                db.session.add(message)
                db.session.commit()
                
                return make_response(jsonify(message), 200 )
            
            elif request.method == 'DELETE':
                db.session.delete(message)
                db.session.commit()
                
                response_body = {
                    "delete_successful": True,
                    "message": "message deleted."
                }
                return make_response(response_body, 200 )
        
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)
