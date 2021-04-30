from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
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
                    admin_email = "pharmasearchuwo@gmail.com"
                    admin_email_pass = "PharmaSearch2021"
                    #new_msg = """Subject: Update Info From User: 
                    #yes
                    #"""
                    
                    try:
                        email_p ="Title:Update Info From User: "
                        newdetail="You have received a new message. Here are the details:"
                        drugcode_p="Requested update Drug Code: "
                        codetype_p="Requested update Code Type: "
                        conent_p="Detailed Message:"
                        new_msg = "\n"+email_p+email+"\n\n"+newdetail+"\n\n"+drugcode_p+drugcode+"\n\n"+codetype_p+codetype+"\n\n"+conent_p+"\n"+content
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(admin_email, admin_email_pass)
                        server.sendmail(admin_email, admin_email, new_msg)
                        server.quit()
                        message = "We have received your request! We will contact to you soon!"
                        return render_template('user_success.html', message = message)
                    except:
                        message = "Error: unable to send the email"
                        return render_template('user_success.html', message = message)
    return render_template('user_success.html', message = message)

if __name__ == '__main__':
    app.run()