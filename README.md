# PharmaSearch Website + Flask + Postgresql
Open the PharmaSearch website: https://pharmasearchuwo.herokuapp.com

Run the code in the local machine:
Make sure you have installed postgresql, python 3.7.0+, and heorku CLI
1. Download the code from Heroku
2. Export the sql file from Heroku postgresql and import them to the local postgresql
3. Make sure you have install pipenv. If not, run the following command:
   pip install pipenv
   
   After installed pipenv, under the directory that the code store, run the following command:
   pipenv shell
4. Set up your local postgresql. Change the value of variable ENV to dev at line 18 in app.py, and change the app configuration of sqlalchemy database uri at line 22 in app.py. 
   
   The value of app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:<database_password>@<username,e.g.localhost>/<database_name>'
5. Run the flask app in the local machine, run the following command:
   python app.py
  
