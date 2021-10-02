from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow
import os
from pprint import pprint

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    date_created = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self, name, email):
        self.name = name
        self.email = email
    

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id","name","email","date_created", "_links")

    # Smart hyperlinking
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("single_product", id="<id>"), "collection": ma.URLFor("product")}
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
@app.route('/', methods=['GET'])
def product():
    all_products = Product.query.all()
    result = users_schema.dump(all_products)
    return jsonify(result)

@app.route('/<id>', methods=['GET'])
def single_product(id):
    single_product = Product.query.get(id)
    return user_schema.jsonify(single_product)
     

@app.route('/', methods=['POST'])
def addProduct():
    name  = request.json['name']
    email = request.json['email']
  
    new_product  = Product(name=name,email=email)
    if Product.query.filter_by(email=email).count() == 0:
        db.session.add(new_product)
        db.session.commit()
        return user_schema.jsonify(new_product)
    else:
        return "Email already exist"
        
    
@app.route('/<id>', methods=['PUT'])
def update(id):
    update_product = Product.query.get(id)
    name  = request.json['name']
    email = request.json['email']
    update_product.name = name
    update_product.email = email
    db.session.commit()
    return user_schema.jsonify(update_product)
        
        
       
        
    

   

if __name__ == '__main__':
    app.run(debug=True)