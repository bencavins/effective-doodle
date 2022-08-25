from flask import Flask, render_template, request
from twitoff.models import DB, User, Tweet
import os
from twitoff.predict import predict_user

from twitoff.twitter import add_or_update_user


def create_app():
    app = Flask(__name__)

    # DB config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route("/")
    def root():
        # query db for users
        users = User.query.all()
        return render_template('base.html', title="HOME", users=users)

    @app.route('/test')
    def test():
        return '<p>This  is a test</p>'

    @app.route('/user', methods=['POST'])
    def add_user():
        username = request.values['user_name']
        add_or_update_user(username)
        user = User.query.filter(User.username == username).one()
        return render_template(
            'user.html', 
            title=username, 
            message='User added successfully!',
            tweets=user.tweets,
        )
    
    @app.route('/user/<name>')
    def user(name=None):
        user = User.query.filter(User.username == name).one()
        return render_template(
            'user.html', 
            title=name, 
            message='User added successfully!',
            tweets=user.tweets,
        )
    
    @app.route('/compare', methods=['POST'])
    def compare():
        username0 = request.values['user0']
        username1 = request.values['user1']
        hypo_tweet_text = request.values['tweet_text']

        if username0 == username1:
            message = 'Cannot compare a user to themselves'
        else:
            prediction = predict_user(username0, username1, hypo_tweet_text)
            if prediction:
                predicted_user = username1
            else:
                predicted_user = username0
            message = f'This tweet is more likely written by {predicted_user}'

        return render_template('prediction.html', title='Prediction', message=message)
    
    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return """The db has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to Reset</a>
        <a href='/populate'>Go to Populate</a>"""
    
    @app.route('/update')
    def update():
        users = User.query.all()
        for user in users:
            add_or_update_user(user.username)
        return """Users have been updated
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to Reset</a>
        <a href='/populate'>Go to Populate</a>"""
    
    @app.route('/populate')
    def populate():
        user1 = User(id=1, username='ben')
        DB.session.add(user1)
        tweet1 = Tweet(id=1, text='this is a tweet', user=user1)
        DB.session.add(tweet1)
        DB.session.commit()
        return """The db has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to Reset</a>
        <a href='/populate'>Go to Populate</a>"""
    
    return app