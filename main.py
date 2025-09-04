from dbm import error

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

def json_form(cafes):
        list_ = []
        for cafe in cafes :
            if hasattr(cafe, '__table__'):
                 list_.append({c.name: getattr(cafe, c.name) for c in cafe.__table__.columns})

        return list_

# HTTP GET - Read Record
def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return False

@app.route("/random",methods=['GET'])
def get_cafes():
    cafes = Cafe.query.all()
    return  jsonify(json_form(cafes))

@app.route("/random/<int:id>",methods=['GET'])
def get_cafe(id):
    cafe = db.get_or_404(Cafe,id)
    return  jsonify({c.name: getattr(cafe, c.name) for c in cafe.__table__.columns})

# HTTP POST - Create Record
@app.route("/add",methods=['POST'])
def add():
    data = request.get_json()  # expects JSON body with same keys as model
    # create Cafe object using unpacking (**dict)
    new_cafe = Cafe(
        name=data.get("name"),
        map_url=data.get("map_url"),
        img_url=data.get("img_url"),
        location=data.get("location"),
        seats=data.get("seats"),
        has_toilet=str_to_bool(data.get("has_toilet")),
        has_wifi=str_to_bool(data.get("has_wifi")),
        has_sockets=str_to_bool(data.get("has_sockets")),
        can_take_calls=str_to_bool(data.get("can_take_calls")),
        coffee_price=data.get("coffee_price")
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(message="Cafe added successfully!", id=new_cafe.id)
# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record
@app.route("/delete/<int:id>",methods=['DELETE'])
def delete(id):
   try:
        cafe = db.get_or_404(Cafe,id)
        db.session.delete(cafe)
        db.session.commit()
        return jsonify({"code":"successful"})
   except:
        return jsonify({"code":"unsuccessful"})
@app.route('/edit/<int:id>',methods=['PATCH'])
def edit(id):
    try:
        form_ = request.get_json()
        cafe = db.get_or_404(Cafe,id)
        cafe.coffee_price = form_.get('new_price')
        db.session.commit()
        return jsonify({"success":'operation done'})
    except Exception as e:
        return jsonify(error=str(e)),400
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port)
