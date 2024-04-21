class DataInsightsConstants:
    try:
        HOUSE_HOLD_FILE_PATH = "/tmp/static/UploadFiles/Households"
        TRANSACTION_FILE_PATH = "/tmp/static/UploadFiles/Transactions"
        UPLOAD_FILE_PATH = "/tmp/static/UploadFiles/Products"
        ALLOWED_EXTENSIONS = ['csv']
        BASE_LOGIN_QUERY = "SELECT firstname,lastname,email  FROM users WHERE username  ='{}' AND password_hash = '{}'"
        RETRIEVE_USER_INFO_QUERY = "SELECT *  FROM users WHERE username  ='{}'"
        ALREADY_REGISTERED = "Looks like you hit your head, You are already registered and you forgot about it!"
        NEW_USER_INSERT_QUERY = """INSERT INTO users (username, password_hash, firstname, lastname, email) values (
        %s, %s, %s, %s, %s) """
        EXTRACT_USER_INFO = "SELECT firstname, lastname, email FROM users WHERE username  = '{}' AND password_hash " \
                            "='{}'"
        UPLOAD_RETRY_MESSAGE = "Please upload file again in a bit."
        DATABASE_CONNECTION_OBJECT = {
        'host': '********',
        'user': '*******',
        'password': '******',
        'database': '*******'
        }
        HOUSE_HOLD_INSERT = "INSERT INTO households (HSHD_NUM,L,AGE_RANGE,MARITAL,INCOME_RANGE,HOMEOWNER,HSHD_COMPOSITION,HH_SIZE,CHILDREN) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        TRANSACTIONS_INSERT = "INSERT INTO transactions (BASKET_NUM,HSHD_NUM,PURCHASE_,PRODUCT_NUM,SPEND,UNITS,STORE_R,WEEK_NUM,YEAR_NUM) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        PRODUCTS_INSERT = "INSERT INTO products (PRODUCT_NUM,DEPARTMENT,COMMODITY,BRAND_TY,NATURAL_ORGANIC_FLAG) VALUES (%s,%s,%s,%s,%s)"
    except Exception as e:
        print("DataInsightsConstants: ")
        raise e
