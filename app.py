from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key='4093c13c20c9b3f8b803d8db1b6c80bf'

@app.before_request
def assign_session_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Assign unique session ID


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "todo.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db = SQLAlchemy(app)

class Todo(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(200), nullable=False)
    desc= db.Column(db.String(500), nullable=False)
    date_created= db.Column(db.DateTime,default=datetime.utcnow)
    session_id=db.Column(db.String(100),nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route('/',methods=['GET','POST'])
def home():
    if request.method=="POST":
        title = request.form['title']
        desc = request.form['desc']
        todo= Todo(title=title, desc=desc)#type:ignore
        db.session.add(todo)
        db.session.commit()
    
    allTodo = Todo.query.filter_by(session_id=session['user_id']).all()
    return render_template('index.html',allTodo=allTodo)


@app.route('/update/<int:sno>',methods=['GET','POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno, session_id=session['user_id']).first_or_404()
    if request.method=="POST":
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title=title # type: ignore
        todo.desc= desc #type: ignore
        db.session.add(todo)
        db.session.commit()
        return redirect('/')

    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno,session_id=session['user_id']).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)