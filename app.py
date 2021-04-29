from flask import Flask, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

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
            if db.session.query(Admin).filter(Admin.USERNAME == username).filter(Admin.PASSWORD == password).count() != 0:
                session['loggedin'] = True
                session['username'] = username
                #result = db.session.query(Admin).filter(Admin.USERNAME == username).filter(Admin.PASSWORD == password).one()
                #result.LOGGEDIN = "True"
                #db.session.commit()
            else:
                message = "Incorrect username/password!"
    return render_template('admin_home.html', message = message)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return render_template('index.html')

@app.route('/adminHome')
def admin_Home():
    if 'loggedin' in session:
        return render_template('admin_home.html', username = session['username'])
    return render_template('admin_login.html')

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

if __name__ == '__main__':
    app.run()