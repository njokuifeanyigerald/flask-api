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
    name =db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
    

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id","name","description", "price","qty","date_created", "_links")

    # Smart hyperlinking
    # _links = ma.Hyperlinks(
    #     {"self": ma.URLFor("user_detail", id="<id>"), "collection": ma.URLFor("users")}
    # )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
@app.route('/product', methods=['GET'])
def product():
    all_products = Product.query.all()
    result = users_schema.dump(all_products)
    return jsonify(result)

@app.route('/product/<id>', methods=['GET'])
def single_product():
    single_product = Product.query.get(id)
    return user_schema.jsonify(single_product)
     

@app.route('/product', methods=['POST'])
def addProduct():
    name  = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    new_product  = Product(name=name,description=description,price=price,qty=qty)
    if Product.query.filter_by(name=name).count() == 0:
        db.session.add(new_product)
        db.session.commit()
        return user_schema.jsonify(new_product)
    else:
        return "name already exist"
        
    



if __name__ == '__main__':
    app.run(debug=True)