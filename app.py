from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow
import os
from pprint import pprint


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

#database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#referencing SQLAlchemcy
db = SQLAlchemy(app)

#referencing marshmallow
ma = Marshmallow(app)

#model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    date_created = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self, name, email):
        self.name = name
        self.email = email
    

class UserSchema(ma.Schema):
    class Meta:
        #Fields to expose
        fields = ("id","name","email","date_created", "_links")

    #Smart hyperlinking
    _links = ma.Hyperlinks(
    #make sure your function names are the same like 
    #interms of single data fucntion(e.g def singleUser: is singleUser for "self")
    #and many data fucntion(e.g def home: is called home in the "collection")
    #if not there will be an error in the smart hyperlinking
        {"self": ma.URLFor("singleUser", id="<id>"), "collection": ma.URLFor("home")}
        
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)

#get all users
@app.route('/', methods=['GET'])
def home():
    all_Users = User.query.all()
    result = users_schema.dump(all_Users)
    return jsonify(result)

#get a particular user
@app.route('/<id>', methods=['GET'])
def singleUser(id):
    single_User = User.query.get(id)
    return user_schema.jsonify(single_User)
     
#add user
@app.route('/add', methods=['POST'])
def addUser():
    name  = request.json['name']
    email = request.json['email']
  
    new_User  = User(name=name,email=email)
    if User.query.filter_by(email=email).count() == 0:
        db.session.add(new_User)
        db.session.commit()
        return user_schema.jsonify(new_User)
    else:
        return "Email already exist"
        
#update the user  
@app.route('/<id>', methods=['PUT'])
def updateUser(id):
    update_User = User.query.get(id)
    name  = request.json['name']
    email = request.json['email']
    update_User.name = name
    update_User.email = email
    db.session.commit()
    return user_schema.jsonify(update_User)
        
        
       
        
    

   

if __name__ == '__main__':
    app.run(debug=True)