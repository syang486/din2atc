from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_mail import Mail, Message
import smtplib
import re

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/psearch'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kwccbaggatldge:00f9e126c274a545c81945fa20dcc0b7a0cfd13e7c184cd58dec1b732434294f@ec2-107-22-83-3.compute-1.amazonaws.com:5432/dboour5eut0e35'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)
Drug = Base.classes.drug
Company = Base.classes.company
Ingredient = Base.classes.ingred
Package = Base.classes.package
Pharm = Base.classes.pharm
Proute = Base.classes.proute
Pstatus = Base.classes.pstatus
Schedule = Base.classes.schedule
Ther = Base.classes.ther
Admin = Base.classes.admin

admin_email = db.session.query(Admin.EMAIL).all()
admin_email_pass = db.session.query(Admin.EMAILPASS).all()


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = admin_email
app.config['MAIL_PASSWORD'] = admin_email_pass
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/adminLogin')
def adminLogin():
    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            if db.session.query(Admin).filter(Admin.USERNAME == username).filter(Admin.PASSWORD == password).count() == 0:
                message = "Incorrect username/password!"
                return render_template('admin_login.html', message = message)
    return render_template('admin_home.html', username = username)

@app.route('/logout')
def logout():
    return render_template('index.html')

@app.route('/adminHome')
def adminHome():
    username = db.session.query(Admin.USERNAME).one()
    username = username[0]
    return render_template('admin_home.html', username = username)

@app.route('/adminProfile')
def adminProfile():
    users = db.session.query(Admin).all()
    return render_template('admin_profile.html', users = users)

@app.route('/ViewData')
def ViewData():
    return render_template('view_data.html', message="One of Brand Name or DIN Code or TC_ATC Code is required!")

@app.route('/ModifyData', methods=['GET','POST'])
def ModifyData():
    message = "One of Brand Name or DIN Code or TC_ATC Code is required!"
    if request.method == 'POST':
        message = "success!"
    return render_template('modify_data.html', message=message)

@app.route('/ManageProfile')
def ManageProfile():
    return render_template('manage_profile.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/researcher', methods=['GET', 'POST'])
def researcher():
    if request.method == 'POST':
        din = request.form["researcher-din"]
        atc = request.form["researcher-atc"]
        if din == '' and atc == '':
            message = "⚠️Please enter either DIN or ATC Code."
            return render_template('researcher_result.html', message = message)
        elif din != '' and atc == '':
            while(din[0] == '0'):
                din = din[1:]
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).count() == 0:
                message = "⚠️Sorry, Please enter the correct DIN Code."
                return render_template('researcher_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).distinct().all()
            return render_template('researcher_result.html', results = results, results_ingred = results_ingred)
        elif din == '' and atc != '':
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Drug, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).count() == 0:
                message = "⚠️Sorry, Please enter the correct ATC Code."
                return render_template('researcher_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Drug, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).distinct().all()
            return render_template('researcher_result.html', results = results, results_ingred = results_ingred)            
        else:
            while(din[0] == '0'):
                din = din[1:]
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Drug, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).count() == 0:
                message = "⚠️Sorry, Please enter the correct DIN or ATC Code."
                return render_template('researcher_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER).join(Drug, Drug.DRUG_CODE == Ther.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == atc).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din).distinct().all()
            return render_template('researcher_result.html', results = results, results_ingred = results_ingred)
    return render_template('researcher_result.html')

@app.route('/pharmacist', methods=['GET', 'POST'])
def pharmacist():
    if request.method == 'POST':
        drug_name = request.form["pharmacist-drug_name"].upper()
        din_atc = request.form["pharmacist-din_atc"]
        if drug_name == '' and din_atc == '':
            message = "⚠️Please enter either Drug Name or DIN or ATC Code."
            return render_template('pharmacist_result.html', message = message)
        elif drug_name != '' and din_atc == '':
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).count() == 0:
                message = "⚠️Sorry, Please enter the correct Drug Name."
                return render_template('pharmacist_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            return render_template('pharmacist_result.html', results = results, results_ingred = results_ingred)
        elif drug_name == '' and din_atc != '':
            if(din_atc.isnumeric()):
                while(din_atc[0] == '0'):
                    din_atc = din_atc[1:]
                if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).count() == 0:
                    message = "⚠️Sorry, Please enter the correct DIN Code."
                    return render_template('pharmacist_result.html', message = message)
                results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).distinct().all()
                results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).distinct().all()
                return render_template('pharmacist_result.html', results = results, results_ingred = results_ingred)
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).count() == 0:
                message = "⚠️Sorry, Please enter the correct ATC Code."
                return render_template('pharmacist_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).distinct().all()
            return render_template('pharmacist_result.html', results = results, results_ingred = results_ingred)    
        else:
            if(din_atc.isnumeric()):
                while(din_atc[0] == '0'):
                    din_atc = din_atc[1:]
                if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).count() == 0:
                    message = "⚠️Sorry, Please enter the correct Drug Name or DIN Code."
                    return render_template('pharmacist_result.html', message = message)
                results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).distinct().all()
                results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Drug.DRUG_IDENTIFICATION_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).distinct().all()
                return render_template('pharmacist_result.html', results = results, results_ingred = results_ingred)
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).count() == 0:
                message = "⚠️Sorry, Please enter the correct Drug Name or ATC Code."
                return render_template('pharmacist_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Drug.DRUG_IDENTIFICATION_NUMBER, Ther.TC_ATC_NUMBER, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Package.PRODUCT_INFORMATION, Drug.CLASS, Schedule.PSCHEDULE).join(Ther, Drug.DRUG_CODE == Ther.DRUG_CODE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Package, Drug.DRUG_CODE == Package.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Ther.TC_ATC_NUMBER == din_atc).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            return render_template('pharmacist_result.html', results = results, results_ingred = results_ingred)             
    return render_template('pharmacist_result.html')

@app.route('/patient', methods=['GET', 'POST'])
def patient():
    if request.method == 'POST':
        drug_name = request.form["patinet-drug_name"].upper()
        if drug_name == '':
            message = "⚠️Please enter Drug Name."
            return render_template('patient_result.html', message = message)
        else:
            if db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Schedule.PSCHEDULE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).count() == 0:
                message = "⚠️Sorry, Please enter the correct Drug Name."
                return render_template('patientt_result.html', message = message)
            results = db.session.query(Drug.DRUG_CODE, Drug.BRAND_NAME, Company.COMPANY_NAME, Pharm.PHARMACEUTICAL_FORM, Schedule.PSCHEDULE).join(Company, Drug.DRUG_CODE == Company.DRUG_CODE).join(Pharm, Drug.DRUG_CODE == Pharm.DRUG_CODE).join(Schedule, Drug.DRUG_CODE == Schedule.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            results_ingred = db.session.query(Drug.DRUG_CODE, Ingredient.INGREDIENT, Ingredient.STRENGTH).join(Drug, Drug.DRUG_CODE == Ingredient.DRUG_CODE).filter(Drug.BRAND_NAME == drug_name).distinct().all()
            return render_template('patient_result.html', results = results, results_ingred = results_ingred)
    return render_template('patient_result.html')


@app.route('/userUpdate', methods=['GET', 'POST'])
def userUpdate():
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        drugcode = request.form['drugcode']
        codetype = request.form['codetype']
        content = request.form['subject']
        if email == '':
            if drugcode == '' and content == '':
                    message = "⚠️Please fill out all required field!"
            elif drugcode != '' and content == '':
                message = "⚠️Please fill out Email Address and Up-to-date Information!"
            elif drugcode == '' and content != '':
                message = "⚠️Please fill out Email Address and Drug Code!"
            else:
                message = "⚠️Please fill out Email Address!"
        else:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = "⚠️Invalid email address!"
            else:
                if drugcode == '' and content == '':
                    message = "⚠️Please fill out Drug Code and Up-to-date Information!"
                elif drugcode != '' and content == '':
                    message = "⚠️Please fill out Up-to-date Information!"
                elif drugcode == '' and content != '':
                    message = "⚠️Please fill out Drug Code!"
                else:
                    results = db.session.query(Admin.EMAIL).all()
                    admin_email = results[0][0]
                    results_pass = db.session.query(Admin.EMAILPASS).all()
                    admin_email_pass = results_pass[0][0]
                    # title = "Update Request From User: " + email
                    # msg = Message(title, sender = email, recipients = [admin_email])
                    # msg.body = "You have received a new message. Here are the details:\n Requested update drugcode:  \n " + drugcode + "\nRequested update code type:" + codetype + "\n Detailed message:" + content +"\n"
                    # mail.send(msg)
                    # title1 = "Thank you for using PharmaSearch"
                    # msg1 = Message(title1, sender = admin_email, recipients = [email])
                    # msg1.body = "<html><h1>Hi, "+email+"</h1><p>Thank you for using PharmaSearch. We have received your request! We will contact to you soon!</p><p>Here is the copy of your submitted request:\n Requested update drugcode:  \n " + drugcode + "\nRequested update code type:" + codetype + "\n Detailed message:" + content +"\n</p>"
                    # mail.send(msg1)
                    # message = "We have received your request! We will contact to you soon!"
                    new_msg = "Email: " + email + "\n" + "Drug code: " + drugcode + "\n" + "Code type: " + codetype + "\n" + "Content: " + content + "\n"
                    server = smtplib.SMTP("smtp.gmail.com")
                    server.starttls()
                    server.login(admin_email, admin_email_pass)
                    server.sendmail(admin_email, admin_email, new_msg)
                    message = "success!"
    return render_template('user_success.html', message = message)
        
@app.route('/adminUpdate', methods=['POST', 'GET'])
def adminUpdate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        emailpass = request.form['emailpass']
        users = db.session.query(Admin).filter(Admin.ID == 1).one()
        if username != '':
            users.USERNAME = username
            db.session.commit()
        if password != '':
            users.PASSWORD = password
            db.session.commit()
        if email != '':
            users.EMAIL = email
            db.session.commit()
        if emailpass != '':
            users.EMAILPASS = emailpass
            db.session.commit()
    users = db.session.query(Admin).one()
    return redirect(url_for('adminProfile'))

@app.route('/searchData', methods=['GET', 'POST'])
def searchData():
    return render_template('view_result.html')


if __name__ == '__main__':
    app.run()