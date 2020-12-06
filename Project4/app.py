from flask import Flask, render_template, request
import requests
from Project4 import main_functions
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField

app = Flask(__name__)
app.config["SECRET_KEY"] = "include_a_strong_secret_key"
app.config["MONGO_URI"] = "mongodb+srv://tonyadmin:05210521@cluster0.ipbwd.mongodb.net/db?retryWrites=true&w=majority"
mongo = PyMongo(app)


class Expenses(FlaskForm):
    description = StringField('Description')
    category = SelectField('Category', choices=[("Rent", "Rent"),
                                                ("Water", "Water"),
                                                ("Beer", "Beer"),
                                                ("Child Support", "Child Support"),
                                                ("Casino", "Casino")])
    cost = DecimalField('cost', )
    currency = SelectField('Currency', choices=[("USD", "US Dollar"),
                                                ("AUD", "Australian Dollar"),
                                                ("CAD", "Canadian Dollar"),
                                                ("MXN", "Mexican Peso")])
    date = DateField('date', format='%Y-%m-%d')


def get_total_expenses(category):
    catquery = {"Category": category}
    cat_expenses = mongo.db.expenses.find(catquery)
    cattotal_cost = 0
    for i in cat_expenses:
        cattotal_cost += float(i["Cost"])
    return cattotal_cost


def currency_converter(cost, currency):
    url = "http://api.currencylayer.com/live?access_key=347e37558aaa2d0f7202f4363e3f8b90&currencies=USD,AUD,CAD,MXN"
    response = requests.get(url).json()
    main_functions.save_to_file(response, "JSON_Files/currency.json")
    currencyinfo = main_functions.read_from_file("JSON_Files/currency.json")
    #print("selected Currency is" + currency)
    #print("current cost is " + cost + "in" + currency)
    currencystring = "USD" + currency
    if currency == "USD":
        return cost
    else:
        USDexchangerate = currencyinfo["quotes"][currencystring]
        converted_cost = float(cost) / float(USDexchangerate)
        formattedcost = "{:.2f}".format(converted_cost)
        #print("Cost is now" + formattedcost + "in USD")

    ### YOUR TASK IS TO COMPLETE THIS FUNCTION
        return converted_cost


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["Cost"])

    expensesByCategory = [("Rent", get_total_expenses("Rent")),
                          ("Water", get_total_expenses("Water")),
                          ("Beer", get_total_expenses("Beer")),
                          ("Child Support", get_total_expenses("Child Support")),
                          ("Casino", get_total_expenses("Casino"))]
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    # INCLUDE THE FORM
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        # INSERT ONE DOCUMENT TO THE DATABASE
        Desc = request.form["description"]
        Cat = request.form["category"]
        Cos = request.form["cost"]
        Cur = request.form["currency"]
        Date1 = request.form["date"]
        convertedcurrency = currency_converter(Cos, Cur)
        datainsert = {'Description': Desc, 'Category': Cat, 'Cost': convertedcurrency,
                      'Date': Date1}
        expenses = mongo.db.expenses
        expenses.insert_one(datainsert)
        # CONTAINING THE DATA LOGGED BY THE USER
        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)


app.run()
