from decimal import *
from flask import Flask, request, render_template
import json
import mysql.connector
from mysql.connector import errorcode
import os
import pandas as pd
import shutil
from werkzeug.utils import secure_filename
from constants.constants import DataInsightsConstants

app = Flask(__name__)
app.config.from_object(__name__)

app.config['uploadFolderHouseholds'] = DataInsightsConstants.HOUSE_HOLD_FILE_PATH
app.config['uploadFolderTransactions'] = DataInsightsConstants.TRANSACTION_FILE_PATH
app.config['uploadFolderProducts'] = DataInsightsConstants.UPLOAD_FILE_PATH


def makeRequiredDirectories():
    try:
        if not os.path.exists(app.config['uploadFolderHouseholds']):
            os.makedirs(app.config['uploadFolderHouseholds'], 0o777)
        else:
            shutil.rmtree(app.config['uploadFolderHouseholds'])
            os.makedirs(app.config['uploadFolderHouseholds'], 0o777)

        if not os.path.exists(app.config['uploadFolderTransactions']):
            os.makedirs(app.config['uploadFolderTransactions'], 0o777)
        else:
            shutil.rmtree(app.config['uploadFolderTransactions'])
            os.makedirs(app.config['uploadFolderTransactions'], 0o777)

        if not os.path.exists(app.config['uploadFolderProducts']):
            os.makedirs(app.config['uploadFolderProducts'], 0o777)
        else:
            shutil.rmtree(app.config['uploadFolderProducts'])
            os.makedirs(app.config['uploadFolderProducts'], 0o777)

    except Exception as e:
        print("In makeRequiredDirectories: ", e)
        raise e


makeRequiredDirectories()


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, Decimal):
                return str(obj)

            return json.JSONEncoder.default(self, obj)
        except Exception as e:
            print("In default: ", e)
            raise e


def validateFileExtension(filename):
    try:
        return filename.split('.')[-1] in DataInsightsConstants.ALLOWED_EXTENSIONS
    except Exception as e:
        print("In validateFileExtension: ", e)
        raise e


@app.route("/")
def base():
    try:
        return render_template('login.html')
    except Exception as e:
        print("In base: ", e)
        raise e


@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        message = ""
        if request.method == 'POST' and str(request.form['username']) != "" and str(request.form['password']) != "":
            username = str(request.form['username'])
            password = str(request.form['password'])

            result = executeSelectQuery(DataInsightsConstants.BASE_LOGIN_QUERY.format(username, password))

            if result.shape[0] != 0:
                print("Logged in Successfully")
                return render_template('HomePage.html', message=message)
            else:
                message = 'Imposter! Invalid Credentials!!!!'

        elif request.method == 'POST':
            message = 'Please enter Credentials'
        return render_template('login.html', message=message)
    except Exception as e:
        print("In login: ", e)
        raise e


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        return render_template('HomePage.html')
    except Exception as e:
        print("In dashboard: ", e)
        raise e


@app.route('/uploadDatasets', methods=['GET', 'POST'])
def uploadDatasets():
    try:
        return render_template('UploadData.html')
    except Exception as e:
        print("In uploadDatasets: ", e)
        raise e


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    try:
        message = ""
        conn = connectToDataBase()
        cursor = conn.cursor()

        if request.method == 'POST' and str(request.form['username']) != "" and str(
                request.form['password']) != "" and str(
            request.form['firstname']) != "" and str(request.form['lastname']) != "" and str(
            request.form['email']) != "":
            username = str(request.form['username'])
            password = str(request.form['password'])
            firstname = str(request.form['firstname'])
            lastname = str(request.form['lastname'])
            email = str(request.form['email'])

            result = executeSelectQuery(DataInsightsConstants.RETRIEVE_USER_INFO_QUERY.format(username))
            if result.shape[0] != 0:
                message = DataInsightsConstants.ALREADY_REGISTERED
            else:
                insertQuery = cursor.execute(
                    DataInsightsConstants.NEW_USER_INSERT_QUERY,
                    (username, password, firstname, lastname, email))
                conn.commit()
                cursor.close()
                conn.close()
                extractUserInfo = executeSelectQuery(DataInsightsConstants.EXTRACT_USER_INFO.format(username, password))
                if extractUserInfo.shape[0] != 0:
                    message = 'User Registration Completed Successfully! Click Login.'
                    return render_template('registrationSuccess.html', message=message)
        elif request.method == 'POST':
            message = 'Some of the fields are missing!!'
        return render_template('registration.html', message=message)
    except Exception as e:
        print("In registration: ", e)
        raise e


@app.route('/searchhhm', methods=['GET', 'POST'])
def searchhhm():
    try:
        return loadTable("10")
    except Exception as e:
        print("In searchhhm: ", e)
        raise e


@app.route('/searchhhmnew', methods=['GET', 'POST'])
def searchhhmnew():
    try:
        if request.method == 'POST' and str(request.form['hshd_num']) != "":
            try:
                response = loadTable(str(request.form['hshd_num']))
            except:
                message = "Valid HSHD_NUM is required!!"
                return render_template('SearchHHM.html', message=message)
        else:
            message = "Valid HSHD_NUM is required!!"
            return render_template('SearchHHM.html', message=message)
        return response
    except Exception as e:
        print("In searchhhmnew: ", e)
        raise e


@app.route('/storeUploadedHouseholdFile', methods=['GET', 'POST'])
def storeUploadedHouseholdFile():
    try:
        message = DataInsightsConstants.UPLOAD_RETRY_MESSAGE
        if request.method == 'POST':
            f = request.files['file']
            if validateFileExtension(f.filename):
                f.save(os.path.join(app.config['uploadFolderHouseholds'],
                                    secure_filename(f.filename)))
                readCsvAndLoadData(os.path.join(app.config['uploadFolderHouseholds'], secure_filename(f.filename)),
                                   "households")
                message = 'file uploaded successfully'
            else:
                message = 'The file extension is not allowed'

        return render_template('UploadData.html', message=message)
    except Exception as e:
        print("In storeUploadedHouseholdFile: ", e)
        raise e


@app.route('/storeUploadedProductFile', methods=['GET', 'POST'])
def storeUploadedProductFile():
    try:
        message = DataInsightsConstants.UPLOAD_RETRY_MESSAGE
        if request.method == 'POST':
            f = request.files['file']
            if validateFileExtension(f.filename):
                f.save(os.path.join(app.config['uploadFolderProducts'],
                                    secure_filename(f.filename)))
                readCsvAndLoadData(os.path.join(app.config['uploadFolderProducts'], secure_filename(f.filename)),
                                   "products")
                message = 'file uploaded successfully'
            else:
                message = 'The file extension is not allowed'

        return render_template('UploadData.html', messageProducts=message)
    except Exception as e:
        print("In storeUploadedProductFile: ", e)
        raise e


@app.route('/storeUploadedTransactionFile', methods=['GET', 'POST'])
def storeUploadedTransactionFile():
    try:
        message = DataInsightsConstants.UPLOAD_RETRY_MESSAGE
        if request.method == 'POST':
            f = request.files['file']
            if validateFileExtension(f.filename):
                f.save(os.path.join(app.config['uploadFolderTransactions'],
                                    secure_filename(f.filename)))
                readCsvAndLoadData(os.path.join(app.config['uploadFolderTransactions'], secure_filename(f.filename)),
                                   "transactions")
                message = 'file uploaded successfully'
            else:
                message = 'The file extension is not allowed'

        return render_template('UploadData.html', messageTransactions=message)
    except Exception as e:
        print("In storeUploadedTransactionFile: ", e)
        raise e


def executeSelectQuery(queryString):
    try:
        conn = connectToDataBase()
        return pd.read_sql(queryString, conn)
    except Exception as e:
        print("In executeSelectQuery: ", e)
        raise e


def loadTable(hshd_num):
    try:
        conn = connectToDataBase()
        cursor = conn.cursor()
        with open('queries/loadData.sql') as fileReader:
            loadDataSql = fileReader.read().format(hshd_num)
        cursor.execute(loadDataSql)
        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('SearchHHMTable.html', data=rows)
    except Exception as e:
        print("In loadTable: ", e)
        raise e


# '''

# '''
def connectToDataBase():
    config = DataInsightsConstants.DATABASE_CONNECTION_OBJECT
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established with the database")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Looks like there is something wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return conn


def readCsvAndLoadData(csvFilePath, dataFrom):
    try:
        conn = connectToDataBase()
        cursor = conn.cursor()
        df = pd.read_csv(csvFilePath)
        df.columns = df.columns.str.replace(' ', '')
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        dfToTuple = list(df.to_records(index=False))
        if dataFrom == 'households':
            for eachTuple in dfToTuple:
                try:
                    cursor.execute(
                        DataInsightsConstants.HOUSE_HOLD_INSERT,
                        (int(eachTuple.HSHD_NUM), str(eachTuple.L), str(eachTuple.AGE_RANGE), str(eachTuple.MARITAL),
                         str(eachTuple.INCOME_RANGE), str(eachTuple.HOMEOWNER), str(eachTuple.HSHD_COMPOSITION),
                         str(eachTuple.HH_SIZE), str(eachTuple.CHILDREN)))
                except Exception as e:
                    print('Failed to upload to ftp: ' + str(e))
        if dataFrom == 'transactions':
            for eachTuple in dfToTuple:
                try:
                    cursor.execute(
                        DataInsightsConstants.TRANSACTIONS_INSERT,
                        (int(eachTuple.BASKET_NUM), int(eachTuple.HSHD_NUM), str(eachTuple.PURCHASE_),
                         int(eachTuple.PRODUCT_NUM), int(eachTuple.SPEND), int(eachTuple.UNITS), str(eachTuple.STORE_R),
                         int(eachTuple.WEEK_NUM), int(eachTuple.YEAR)))
                except Exception as e:
                    print('Failed to upload to ftp: ' + str(e))
        if dataFrom == 'products':
            for eachTuple in dfToTuple:
                try:
                    cursor.execute(
                        DataInsightsConstants.PRODUCTS_INSERT,
                        (int(eachTuple.PRODUCT_NUM), str(eachTuple.DEPARTMENT), str(eachTuple.COMMODITY),
                         str(eachTuple.BRAND_TY),
                         str(eachTuple.NATURAL_ORGANIC_FLAG)))
                except Exception as e:
                    print('Failed to upload to ftp: ' + str(e))
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("In readCsvAndLoadData: ", e)
        raise e


@app.route('/loadDashboard', methods=['GET', 'POST'])
def loadDashboard():
    # First Graph(bar Graph)
    data = executeSelectQuery(
        "Select SUM(b.SPEND) as Spent,a.HH_SIZE as household_Size from households as a inner join transactions as b on a.HSHD_NUM=b.HSHD_NUM group by a.HH_SIZE;");
    data['Spent'] = data['Spent'].astype(str);
    data['household_Size'] = data['household_Size'].astype(str);

    # Second Grapgh(Bar Graph)
    Seconddata = executeSelectQuery(
        "Select SUM(b.SPEND) as spend,a.HH_SIZE as householdsize from households as a inner join transactions as b inner join products as c  on b.PRODUCT_NUM=c.PRODUCT_NUM and a.HSHD_NUM=b.HSHD_NUM and c.DEPARTMENT='FOOD'  group by c.DEPARTMENT,a.HH_SIZE;");
    Seconddata['spend'] = Seconddata['spend'].astype(str);
    Seconddata['householdsize'] = Seconddata['householdsize'].astype(str);

    SeconddataTwo = executeSelectQuery(
        "Select SUM(b.SPEND) as spend,a.HH_SIZE as householdsize from households as a inner join transactions as b inner join products as c  on b.PRODUCT_NUM=c.PRODUCT_NUM and a.HSHD_NUM=b.HSHD_NUM and c.DEPARTMENT='NON-FOOD'  group by c.DEPARTMENT,a.HH_SIZE;");
    SeconddataTwo['spend'] = SeconddataTwo['spend'].astype(str);

    Threedata = executeSelectQuery(
        "Select SUM(b.SPEND) as spend,c.COMMODITY as commodity  from households as a inner join transactions as b inner join products as c  on b.PRODUCT_NUM=c.PRODUCT_NUM and a.HSHD_NUM=b.HSHD_NUM and c.DEPARTMENT='FOOD'  group by c.COMMODITY;");
    Threedata['spend'] = Threedata['spend'].astype(str);
    Threedata['commodity'] = Threedata['commodity'].astype(str);

    Fourthdata = executeSelectQuery(
        "Select sum(SPEND) as spend,YEAR_NUM as year from transactions as a group by a.YEAR_NUM;");
    Fourthdata['spend'] = Fourthdata['spend'].astype(str);
    Fourthdata['year'] = Fourthdata['year'].astype(str);

    return render_template("Dashboard.html", title='Household Size vs Spent', max=17000,
                           titletwo="Spent vs Householdsize vs Product Department",
                           labels=data['household_Size'].values.tolist(), values=data['Spent'].values.tolist(),
                           labelstwo=Seconddata['householdsize'].values.tolist(),
                           valuestwo=Seconddata['spend'].values.tolist(),
                           valuestwotwo=SeconddataTwo['spend'].values.tolist(),
                           titlethree="Spent(Commodity:Food) vs Different Food Items",
                           labelsthree=Threedata['commodity'].values.tolist(),
                           valuesthree=Threedata['spend'].values.tolist(),
                           titlefour="Spent vs YEAR",
                           labelsfour=Fourthdata['year'].values.tolist(),
                           valuesfour=Fourthdata['spend'].values.tolist());


# '''


if __name__ == '__main__':
    app.run()
