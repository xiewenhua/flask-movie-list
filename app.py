from flask import Flask
from flask import url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from flask import request
from flask import redirect
from flask import flash


WIN = sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='dev'
db=SQLAlchemy(app)



@app.context_processor
def inject_user():
    user=User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.cli.command()
def forge():
    """generate fake data."""
    db.create_all()

    name = 'Wenhua Xie'
    movies = [    {'title': 'My Neighbor Totoro', 'year': '1988'},    {'title': 'Dead Poets Society', 'year': '1989'},    {'title': 'A Perfect World', 'year': '1993'},    {'title': 'Leon', 'year': '1994'},    {'title': 'Mahjong', 'year': '1996'},    {'title': 'Swallowtail Butterfly', 'year': '1996'},    {'title': 'King of Comedy', 'year': '1999'},    {'title': 'Devils on the Doorstep', 'year': '1999'},    {'title': 'WALL-E', 'year': '2008'},    {'title': 'The Pork of Music', 'year': '2012'},]
    user=User(name=name)
    db.session.add(user)
    for m in movies:
        movie=Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop.')
def initdb(drop):
    """Initialize the database"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        title=request.form.get('title')
        year=request.form.get('year')
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie=Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created')
        return redirect(url_for('index'))        
    movies=Movie.query.all()
    return render_template('index.html',movies=movies)


@app.route('/user/<name>')
def user_page(name):
    return 'Hello %s!' % name



@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name='Mike'))
    print(url_for('user_page',name='Lisa'))
    print(url_for('test_url_for',num=2))
    return 'Test page'

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(60))
    year=db.Column(db.String(4))