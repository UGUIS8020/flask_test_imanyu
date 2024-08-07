from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import boto3
import uuid

from dotenv import load_dotenv
import os

app = Flask(__name__)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
db.init_app(app)

s3 = boto3.client('s3',
        aws_access_key_id=os.getenv('aws_access_key_id'),
        aws_secret_access_key=os.getenv('aws_secret_access_key'),
        region_name=os.getenv('region_name')
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

@app.route("/")
def index():
    # if request.method == "GET":
        posts = Post.query.all()
        return render_template("index.html", posts=posts)
    # return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")
        file = request.files.get('image_file')
        file_name = uuid.uuid4()
        print(file)
        file.save(file_name)

        Bucket = 'uguis'
        Key = file_name
        s3.upload_file(file_name, Bucket, Key)

        post = Post(title=title, body=body, image_url=file_name)            
        db.session.add(post)
        db.session.commit() 
        return redirect("/")
    else:
        return render_template("create.html")
    
@app.route("/<int:id>/update", methods=["GET", "POST"])
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        return render_template("update.html", post=post)
    
    else:
        post.title = request.form.get("title")
        post.body = request.form.get("body")
        db.session.commit()
        return redirect("/")
    
@app.route("/<int:id>/delete")
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect("/")   


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)