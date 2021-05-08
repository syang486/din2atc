DIN2ATC Website + Flask + Postgresql
Open the PharmaSearch website: https://din2atc.herokuapp.com

Run the code in the local machine: Make sure you have installed postgresql, python 3.7.0+, git bash, and heorku CLI

Download the code from Heroku(check the Deploy section in the app din2atc to see how to download the code from Heroku)

Export the sql file from Heroku postgresql and import them to the local postgresql

Make sure you have install pipenv. If not, run the following command: pip install pipenv

After installed pipenv, under the directory that the code store, run the following command: pipenv shell

Set up your local postgresql. Change the value of variable ENV to dev at line 18 in app.py, and change the app configuration of sqlalchemy database uri at line 22 in app.py.

The value of app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:<database_password>@<username,e.g.localhost>/<database_name>'

Make sure you use pip command to download all components such as psycopg2, psycopg2-binary, flask-sqlalchemy, gunicorn, and flask.

Run the flask app in the local machine, run the following command: python app.py

