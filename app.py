from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    todos = db.relationship('Todo', backref = 'user', lazy = True)
    """
    The line todos = db.relationship('Todo', backref='user', lazy=True) 
    defines a relationship between the User model and the Todo model using SQLAlchemy's relationship feature.

    backref='user': This parameter establishes a reverse relationship from the Todo model back to the User model. 
    It adds a user attribute to the Todo model, allowing you to access the user associated with a specific todo. 
    For example, if you have a todo object, you can access its associated user using todo.user.

    lazy=True, the todos associated with a user will be loaded lazily, 
    meaning they will be fetched from the database only when you access the todos attribute. 
    This can improve performance by reducing unnecessary database queries.
    """

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable= False)

    def __init__(self,title,user_id):
        self.title = title
        self.user_id = user_id

# Routes
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('user_detail.html', user = user)
    else:
        return render_template('404.html'), 404
    
@app.route('/users/<int:user_id>/todos', methods= ['POST'])
def create_todo(user_id):
    title = request.form['title']
    user = User.query.get(user_id)
    if user:
        new_todo = Todo(title, user_id)
        db.session.add(new_todo)
        db.session.commit()

    return redirect(url_for('user_detail', user_id = user_id))

@app.route('/users/<int:user_id>/todos/<int:todo_id>/toggle', methods = ['POST'])
def toggle_todo_completed(user_id, todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        todo.completed = not todo.completed
        db.session.commit()
    
    return redirect(url_for('user_detail', user_id=user_id))

@app.route('/users/<int:user_id>/todos/<int:todo_id>/delete', methods = ['POST'])
def delete_todo(user_id, todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
    
    return redirect(url_for('user_detail', user_id = user_id))

if __name__ == '__main__':
    with app.app_context(): # ensure that the table creation happens within the application context.
        db.create_all()
        app.run(debug = True)