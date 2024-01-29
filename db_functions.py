import pyodbc
from jproperties import Properties

from utils import gen_rand1
from mysql.connector import Error
import mysql.connector as msql
from faker import Faker
import sqlite3
from faker import Faker

configs = Properties()
with open('input.properties', 'rb') as config_file:
    configs.load(config_file)

fake = Faker()
host = str(configs.get("host").data)
username = str(configs.get("username").data)
passwd = str(configs.get("passwd").data)
dbname = str(configs.get("dbname").data)
whichdb = str(configs.get("whichdb").data)
which_location = str(configs.get("whichlocation").data)
server_ms_stage = str(configs.get("server_ms_stage").data)
database_ms_stage = str(configs.get("database_ms_stage").data)
server_ms = str(configs.get("server_ms").data)
database_ms = str(configs.get("database_ms").data)
username_ms = str(configs.get("username_ms").data)
password_ms = str(configs.get("password_ms").data)
server_ms_loc = str(configs.get("server_ms_loc").data)
database_ms_loc = str(configs.get("database_ms_loc").data)
username_ms_loc = str(configs.get("username_ms_loc").data)
password_ms_loc = str(configs.get("password_ms_loc").data)
server_ms_qa = str(configs.get("server_ms_qa").data)
database_ms_qa = str(configs.get("database_ms_qa").data)

def get_db_connection():
    conn = None
    # print(whichdb + which_location)
    if whichdb == 'mysql':
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
    elif whichdb == 'mssql' and which_location == 'remotestage':
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};Server=tcp:' + server_ms_stage + ',1433;Database=' + database_ms_stage + ';Uid=' + username_ms + ';Pwd=' + password_ms + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword')
    elif whichdb == 'mssql' and which_location == 'remote':
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};Server=tcp:' + server_ms + ',1433;Database=' + database_ms + ';Uid=' + username_ms + ';Pwd=' + password_ms + ';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;Authentication=ActiveDirectoryPassword')
    elif whichdb == 'mssql' and which_location == 'remoteqa':
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};Server=tcp:' + server_ms_qa + ',1433;Database=' + database_ms_qa + ';Uid=' + username_ms + ';Pwd=' + password_ms + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword')
    elif whichdb == 'mssql' and which_location == 'local':
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};Server=tcp:' + server_ms_loc + ',1433;Database=' + database_ms_loc + ';Uid=' + username_ms_loc + ';Pwd=' + password_ms_loc + ';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30')
    return conn


def insert_one_record_accounts_table():
    try:
        fake = Faker()
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        ucn = ""
        account_name = ""
        address = ""
        city = ""
        state = ""
        postalcode = ""

        """
        Connect to SQLite db and get random account number.
        """
        con = sqlite3.connect('account_names.db')
        sql = 'SELECT account_name FROM account_names ORDER BY RANDOM() LIMIT 1'
        cur = con.cursor()
        cur.execute(sql)
        record = cur.fetchall()
        account_name = record[0][0]

        """
        Generate random UCN and convert to string.
        """
        random_ucn_int = gen_rand1(1, 99999999)
        ucn = f'{random_ucn_int:08d}'

        address = fake.address()
        city = fake.city()
        state = fake.state()
        postalcode = fake.zipcode()

        if conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT individualUCN FROM accounts WHERE individualUCN = %s", (account_name,))
            # gets the number of rows affected by the command executed
            cursor.fetchall()
            row_count = cursor.rowcount
            # print(\number of affected rows: {}\.format(row_count))
            if row_count == 0:
                # print(\------\)
                sql = "INSERT INTO accounts (individualUCN,hin,accountName,address,city,state,postalCode," \
                      "activeFlag,createdAt,updatedAt) VALUES (%s,NULL,%s,%s,%s,%s,%s,TRUE,NOW(),NOW())"

                cursor1.execute(sql, (ucn, account_name, address, city, state, postalcode))
                # print("Record inserted")
                # the connection is not autocommitted by default, so we
                # must commit to save our changes
                conn.commit()
                return ucn
            else:
                return ""
    except Error as e:
        print("Error while connecting to MySQL", e)
        return ""


def insert_main_accounts_mapping(account_number):
    try:
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT accountUCN FROM main_sub_account_mapping WHERE accountUCN = %s",
                       (account_number,))
        # gets the number of rows affected by the command executed
        cursor.fetchall()
        row_count = cursor.rowcount

        if row_count == 0:
            sql_pr = "INSERT INTO main_sub_account_mapping (accountUCN,parentUCN,createdAt,updatedAt) " \
                     "VALUES (%s,NULL,NOW(),NOW())"

            cursor1.execute(sql_pr, (account_number,))
            # print("Record inserted")
            # the connection is not autocommitted by default, so we
            # must commit to save our changes
            conn.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)


def insert_sub_and_main_accounts_mapping(main_account_number, sub_account_number):
    try:
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT accountUCN FROM main_sub_account_mapping WHERE accountUCN = %s",
                       (sub_account_number,))
        # gets the number of rows affected by the command executed
        cursor.fetchall()
        row_count = cursor.rowcount

        if row_count == 0:
            sql_pr = "INSERT INTO main_sub_account_mapping (accountUCN,parentUCN,createdAt,updatedAt) " \
                     "VALUES (%s,%s,NOW(),NOW())"

            cursor1.execute(sql_pr, (sub_account_number, main_account_number))
            # print("Record inserted")
            # the connection is not autocommitted by default, so we
            # must commit to save our changes
            conn.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)


def insert_sub_accounts_mapping(sub_account_number):
    try:
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT accountUCN FROM main_sub_account_mapping WHERE parentUCN is NULL")
        # gets the number of rows affected by the command executed
        main_accounts = list(cursor.fetchall())

        # print(len(main_accounts))

        random_main_int = gen_rand1(0, len(main_accounts))
        main_map_account = str(main_accounts[random_main_int][0])
        # print(main_map_account)
        # print( main_accounts)
        # print("------------------------------")

        cursor.execute("SELECT accountUCN FROM main_sub_account_mapping WHERE accountUCN = %s",
                       (sub_account_number,))
        # gets the number of rows affected by the command executed
        cursor.fetchall()
        row_count = cursor.rowcount

        if row_count == 0:
            sql_pr = "INSERT INTO main_sub_account_mapping (accountUCN,parentUCN,createdAt,updatedAt) " \
                     "VALUES (%s,%s,NOW(),NOW())"

            cursor1.execute(sql_pr, (sub_account_number, main_map_account))
            # print("Record inserted")
            # the connection is not autocommitted by default, so we
            # must commit to save our changes
            conn.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_all_sub_accounts():
    try:
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT accountUCN FROM main_sub_account_mapping WHERE parentUCN is NOT NULL")
        # gets the number of rows affected by the command executed
        main_accounts = list(cursor.fetchall())

        return main_accounts

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_consignee_assigned_sub_accounts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        # cursor.execute("select database();")
        # record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT DISTINCT(subAccountUCN) FROM consignee_account_mapping")
        # gets the number of rows affected by the command executed
        main_accounts = list(cursor.fetchall())

        return main_accounts

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_all_notification_ids():
    try:
        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)

        cursor.execute("SELECT id FROM notifications")
        # gets the number of rows affected by the command executed
        all_notif_ids = list(cursor.fetchall())

        return all_notif_ids

    except Error as e:
        print("Error while connecting to MySQL", e)


def insert_one_consignee_to_one_account_mapping_table(account_number, consignee_details):
    try:
        # print(consignee_details)
        # print(account_number)

        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)

        if conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT consigneeId FROM consignee_account_mapping WHERE consigneeId = %s",
                           (consignee_details["id"],))
            # gets the number of rows affected by the command executed
            cursor.fetchall()
            row_count = cursor.rowcount
            # print(\number of affected rows: {}\.format(row_count))
            if row_count == 0:
                # print(\------\)
                sql = "INSERT INTO consignee_account_mapping (subAccountUCN,consigneeId,consigneeName," \
                      "consigneeEmail," \
                      "createdAt,updatedAt) VALUES (%s,%s,%s,%s,NOW(),NOW())"

                # print(sql)

                cursor1.execute(sql, (
                    account_number[0], consignee_details["id"], consignee_details["firstName"] + " "
                    + consignee_details["lastName"],
                    consignee_details["email"]))
                # print("Record inserted")
                # the connection is not autocommitted by default, so we
                # must commit to save our changes
                conn.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
        return ""


def insert_consignee_account_mapping_table(account_numbers, consignee_details):
    try:
        # print(consignee_details)
        # print(account_numbers)

        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)

        if conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            for account in account_numbers:

                cursor.execute("SELECT consigneeId FROM consignee_account_mapping WHERE consigneeId = %s "
                               "AND subAccountUCN = %s",
                               (consignee_details["id"], account[0]))
                # gets the number of rows affected by the command executed
                cursor.fetchall()
                row_count = cursor.rowcount
                # print(\number of affected rows: {}\.format(row_count))
                if row_count == 0:
                    # print(\------\)
                    sql = "INSERT INTO consignee_account_mapping (subAccountUCN,consigneeId,consigneeName," \
                          "consigneeEmail," \
                          "createdAt,updatedAt) VALUES (%s,%s,%s,%s,NOW(),NOW())"

                    # print(sql)

                    cursor1.execute(sql, (
                        account[0], consignee_details["id"], consignee_details["firstName"] + " "
                        + consignee_details["lastName"],
                        consignee_details["email"]))
                    # print("Record inserted")
                    # the connection is not autocommitted by default, so we
                    # must commit to save our changes
                    conn.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)


def delete_data_notification_images_material_sbj():
    try:
        conn = get_db_connection()
        if whichdb == 'mysql':
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            cursor.execute("DELETE FROM attachments", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM brf_configurations", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM brf_recall", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM brf_recall_attachments", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM brf_recall_products", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM contact_service_requests", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM custom_action_sets", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM email", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notifications", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_account_mapping", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_action_lists", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_assignees", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_consignee_actions", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_product_images", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM notification_subject_products", ())
            cursor.fetchall()
            cursor.execute("DELETE FROM reopen_notification_service_requests", ())
            cursor.fetchall()
            conn.commit()
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("ALTER SEQUENCE serviceRequestSequence RESTART WITH 1", ())

            cursor.execute("DELETE FROM attachments", ())
            cursor.execute("DBCC CHECKIDENT('attachments', RESEED, 0)", ())

            cursor.execute("DELETE FROM audit_logs", ())
            cursor.execute("DBCC CHECKIDENT('audit_logs', RESEED, 0)", ())

            cursor.execute("DELETE FROM brf_configurations", ())
            cursor.execute("DBCC CHECKIDENT('brf_configurations', RESEED, 0)", ())

            cursor.execute("DELETE FROM brf_recall", ())
            cursor.execute("DBCC CHECKIDENT('brf_recall', RESEED, 0)", ())

            cursor.execute("DELETE FROM brf_recall_attachments", ())
            cursor.execute("DBCC CHECKIDENT('brf_recall_attachments', RESEED, 0)", ())

            cursor.execute("DELETE FROM brf_recall_products", ())
            cursor.execute("DBCC CHECKIDENT('brf_recall_products', RESEED, 0)", ())

            cursor.execute("DELETE FROM contact_service_requests", ())
            cursor.execute("DBCC CHECKIDENT('contact_service_requests', RESEED, 0)", ())

            cursor.execute("DELETE FROM custom_action_sets", ())
            cursor.execute("DBCC CHECKIDENT('custom_action_sets', RESEED, 0)", ())

            cursor.execute("DELETE FROM email", ())
            cursor.execute("DBCC CHECKIDENT('email', RESEED, 0)", ())

            cursor.execute("DELETE FROM faq", ())
            cursor.execute("DBCC CHECKIDENT('faq', RESEED, 0)", ())

            cursor.execute("DELETE FROM inquiry_requests", ())
            cursor.execute("DBCC CHECKIDENT('inquiry_requests', RESEED, 0)", ())

            cursor.execute("DELETE FROM job_schedulers", ())
            cursor.execute("DBCC CHECKIDENT('job_schedulers', RESEED, 0)", ())

            cursor.execute("DELETE FROM notifications", ())
            cursor.execute("DBCC CHECKIDENT('notifications', RESEED, 0)", ())

            cursor.execute("DELETE FROM notification_account_mapping", ())
            cursor.execute("DBCC CHECKIDENT('notification_account_mapping', RESEED, 0)", ())

            cursor.execute("DELETE FROM notification_action_lists", ())
            cursor.execute("DBCC CHECKIDENT('notification_action_lists', RESEED, 0)", ())

            cursor.execute("DELETE FROM notification_assignees", ())
            cursor.execute("DBCC CHECKIDENT('notification_assignees', RESEED, 0)", ())

            # cursor.execute("DELETE FROM notification_consignee_actions", ())
            # cursor.execute("DBCC CHECKIDENT('notification_consignee_actions', RESEED, 0)", ())

            cursor.execute("DELETE FROM notification_product_images", ())
            cursor.execute("DBCC CHECKIDENT('notification_product_images', RESEED, 0)", ())

            cursor.execute("DELETE FROM notification_subject_products", ())
            cursor.execute("DBCC CHECKIDENT('notification_subject_products', RESEED, 0)", ())

            cursor.execute("DELETE FROM reopen_notification_service_requests", ())
            cursor.execute("DBCC CHECKIDENT('reopen_notification_service_requests', RESEED, 0)", ())
            conn.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)


def insert_notifications_actions_list_table(notification_id, notification_type, number_to_insert):
    try:

        conn = msql.connect(host=host, database=dbname, user=username, password=passwd)

        if conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT COUNT(*) FROM action_sets WHERE TYPE = '" + str(notification_type) + "'",
                           ())
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            if int(output[0][0] < int(number_to_insert)):
                exit("number of actions to insert is greater then what is available in the table")
            i = 1
            order_id = 1
            while i <= int(number_to_insert):

                cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s ORDER BY RAND() LIMIT 1",
                               (str(notification_type),))
                # gets the number of rows affected by the command executed
                aoutput = cursor.fetchall()
                action_id = int(aoutput[0][0])

                cursor.execute("SELECT id FROM notifications WHERE adminNotificationId = %s",
                               (str(notification_id),))
                noutput = cursor.fetchall()
                nid = int(noutput[0][0])

                cursor.execute("SELECT * FROM notification_action_lists WHERE notificationID = %s AND actionId= %s",
                               (nid, action_id))
                # gets the number of rows affected by the command executed
                cursor.fetchall()

                row_count = cursor.rowcount
                # print(\number of affected rows: {}\.format(row_count))
                if row_count == 0:
                    # print(\------\)
                    sql = "INSERT INTO notification_action_lists (`checkBoxFlag`, `notificationId`, `order`, " \
                          "`createdAt`, `updatedAt`, `actionId`, `customActionId`) VALUES (0,%s,%s,NOW(),NOW(),%s, " \
                          "NULL)"

                    # print(sql)

                    cursor1.execute(sql, (nid, order_id, action_id))
                    # print("Record inserted")
                    # the connection is not autocommitted by default, so we
                    # must commit to save our changes
                    conn.commit()
                    i = i + 1
                    order_id = order_id + 1

                    sql_ca = "INSERT INTO custom_action_sets (`action`) VALUES (%s)"

                    # print(sql)

                    custom_action_desc = fake.paragraph(nb_sentences=1)

                    cursor1.execute(sql_ca, (custom_action_desc,))
                    # print("Record inserted")
                    # the connection is not autocommitted by default, so we
                    # must commit to save our changes
                    conn.commit()

                    sql_ca_id = "SELECT id from custom_action_sets where action = %s"

                    # print(sql)

                    cursor1.execute(sql_ca_id, (custom_action_desc,))
                    outputid = cursor1.fetchall()

                    caid = outputid[0][0]

                    sql = "INSERT INTO notification_action_lists (`checkBoxFlag`, `notificationId`, `order`, " \
                          "`createdAt`, `updatedAt`, `actionId`, `customActionId`) VALUES (0,%s,%s,NOW(),NOW(),NULL, " \
                          "%s)"

                    # print(sql)

                    cursor1.execute(sql, (nid, order_id, caid))
                    # print("Record inserted")
                    # the connection is not autocommitted by default, so we
                    # must commit to save our changes
                    conn.commit()
                    order_id = order_id + 1


    except Error as e:
        print("Error while connecting to MySQL", e)


def get_notification_type_id_from_db(notification_type):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "SELECT id FROM notification_reference_data WHERE refDataDescription = %s AND refDataType = 'notificationType'",
                (str(notification_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "SELECT id FROM notification_reference_data WHERE refDataDescription = ? AND refDataType = 'notificationType'",
                (str(notification_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_notification_type_from_db(notification_id):
    try:

        conn = get_db_connection()

        # print(whichdb)

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "SELECT refDataDescription FROM notification_reference_data WHERE id = (SELECT `type` FROM notifications WHERE id "
                "= %s)",
                (int(notification_id),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "SELECT refDataDescription FROM notification_reference_data WHERE id = (SELECT type FROM notifications WHERE id "
                "= ?)",
                (int(notification_id),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_rand_predefined_action_id_from_db(notification_type):
    try:

        conn = get_db_connection()

        if conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s ORDER BY RAND() LIMIT 1",
                           (str(notification_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_all_predefined_action_id_from_db(notification_type):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s",
                           (str(notification_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = (SELECT id FROM notification_reference_data where "
                           "refDataDescription = ? and refDataType = 'notificationType')",
                           (str(notification_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_rand_dbid_ref_datas_table(reference_type):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s",
                           (str(reference_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT top 1 id FROM reference_datas WHERE refDataType = ? ORDER BY NEWID()",
                           (str(reference_type),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_rand_notif_id_notifications_table():
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s",
                           (str("reference_type"),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT top 1 adminNotificationId FROM [notifications] where statusId != 4 ORDER BY NEWID()",
                           ())
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_rand_mapped_ucn_nbr(admin_notif_id):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT id FROM action_sets WHERE TYPE = %s",
                           (str("reference_type"),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            return output
        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("SELECT top 1 ucnNo FROM notification_account_mapping where notificationId = (select id "
                           "from notifications where adminNotificationId = ?) ORDER BY NEWID()",
                           (str(admin_notif_id)), )
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()

            if len(output) == 0:
                return "Don't Know"
            else:
                return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_issue_date(notification_id, new_issue_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("UPDATE notifications SET issueDate = %s WHERE id = %s",
                           (str(new_issue_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("UPDATE notifications SET issueDate = ? WHERE id = ?", (new_issue_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_issue_date_account(notification_id, new_issue_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "UPDATE notification_account_mapping SET notificationIssueDate = %s WHERE notificationId = %s",
                (str(new_issue_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("UPDATE notification_account_mapping SET notificationIssueDate = ? WHERE notificationId = ?",
                           (new_issue_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_issue_date_assignees(notification_id, new_issue_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "UPDATE notification_assignees SET notificationIssueDate = %s WHERE notificationId = %s",
                (str(new_issue_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("UPDATE notification_assignees SET notificationIssueDate = ? WHERE notificationId = ?",
                           (new_issue_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_closed_date_account(notification_id, new_issue_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "UPDATE notification_account_mapping SET closedDate = %s WHERE notificationId = %s",
                (str(new_issue_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("UPDATE notification_account_mapping SET closedDate = ? WHERE notificationId = ?",
                           (new_issue_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_closed_date_assignees(notification_id, new_issue_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute(
                "UPDATE notification_assignees SET closedDate = %s WHERE notificationId = %s",
                (str(new_issue_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("UPDATE notification_assignees SET closedDate = ? WHERE notificationId = ?",
                           (new_issue_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def update_notification_closed_date(notification_id, new_closed_date):
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("UPDATE notifications SET closedDate = %s WHERE id = %s",
                           (str(new_closed_date), int(notification_id)))
            # gets the number of rows affected by the command executed
            cursor.fetchall()

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing closed date " + new_closed_date)
            cursor.execute("UPDATE notifications SET closedDate = ? WHERE id = ?", (new_closed_date, notification_id))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            # cursor.fetchall()

        conn.commit()
        conn.close()
        # print("commited")

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_consig_details(email):
    # from consignee_account_mapping table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select consigneeId, consigneeName FROM consignee_account_mapping WHERE consigneeEmail = %s",
                           (str(email),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select consigneeId, consigneeName FROM consignee_account_mapping WHERE consigneeEmail = ?",
                           (str(email),))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_consig_accounts_details(email):
    # from consignee_account_mapping table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select subAccountUCN FROM consignee_account_mapping WHERE consigneeEmail = %s",
                           (str(email),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select subAccountUCN FROM consignee_account_mapping WHERE consigneeEmail = ?",
                           (str(email),))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_all_notif_id_per_account(account):
    # from notification_account_mapping table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select notificationId FROM notification_account_mapping WHERE ucnNo = %s",
                           (str(account),))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select notificationId FROM notification_account_mapping WHERE ucnNo = ?", (str(account),))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_compname_per_notif_id(notif_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select company FROM notifications WHERE id = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select company FROM notifications WHERE id = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_admin_notif_id_per_notif_id(notif_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select company FROM notifications WHERE id = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select adminNotificationId FROM notifications WHERE id = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_notif_name_per_notif_id(notif_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select company FROM notifications WHERE id = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select name FROM notifications WHERE id = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_account_name_per_ucn_id(account_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select company FROM notifications WHERE id = %s",
                           (account_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select accountName FROM accounts WHERE individualUCN = ?", (account_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_attachment_per_notif_id(notif_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select attachmentFlag FROM brf_configurations WHERE notificationId = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select attachmentFlag FROM brf_configurations WHERE notificationId = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_shipping_label_per_notif_id(notif_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select shippingLabelFlag FROM brf_configurations WHERE notificationId = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select shippingLabelFlag FROM brf_configurations WHERE notificationId = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_db_id_per_unique_map_id(unique_map_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select id FROM notification_account_mapping WHERE uniqueMappingId = %s",
                           (unique_map_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select id FROM notification_account_mapping WHERE uniqueMappingId = ?", (unique_map_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_prf_recall_db_id_per_unique_account_map_id(unique_map_id):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select id FROM notification_account_mapping WHERE uniqueMappingId = %s",
                           (unique_map_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select id FROM brf_recall WHERE uniqueMappingId = ?", (unique_map_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_db_id_per_assignee_notification(notif_id, assignee_email):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select id FROM notification_assignees WHERE notificationId = %s and email = %s and "
                           "completedDate is NULL",
                           (notif_id, assignee_email,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            row_count = cursor.rowcount
            if row_count == 0:
                return -1
            else:
                return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select id FROM notification_assignees WHERE notificationId = ? and email = ? and "
                           "completedDate is NULL",
                           (notif_id, assignee_email,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            row_count = cursor.rowcount
            if row_count == 0:
                return -1
            else:
                return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_otp_per_assignee_notification(notif_id, assignee_email):
    # from notifications table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select COALESCE(otp,-1) FROM notification_assignees WHERE notificationId = %s and email = "
                           "%s and"
                           "completedDate is NULL",
                           (notif_id, assignee_email,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            row_count = cursor.rowcount
            if row_count == 0:
                return -1
            else:
                return output[0][0]

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select COALESCE(otp, -1) FROM notification_assignees WHERE notificationId = ? and email = "
                           "? and completedDate is NULL", (notif_id, assignee_email,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            row_count = cursor.rowcount
            if row_count == 0:
                return -1
            else:
                return output[0][0]

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_accounts_per_notif_id(notif_id):
    # from notification_account_mapping table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select ucnNo FROM notification_account_mapping WHERE notificationId = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select ucnNo FROM notification_account_mapping WHERE notificationId = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_action_ids_per_notif_id(notif_id):
    # from notification_action_lists table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select id FROM notification_action_lists WHERE notificationId = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute("select id FROM notification_action_lists WHERE notificationId = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_assignees_per_notif_id(notif_id):
    # from notification_assignees table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)
            email_list = []

            cursor.execute("select email FROM notification_assignees WHERE notificationId = %s",
                           (notif_id,))
            # gets the number of rows affected by the command executed
            for row in cursor:
                for field in row:
                    email_list.append(field)

            return email_list

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            email_list = []

            cursor.execute("select email FROM notification_assignees WHERE notificationId = ?", (notif_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            for row in cursor:
                for field in row:
                    email_list.append(field)

            return email_list

    except Error as e:
        print("Error while connecting to MySQL", e)


def get_consignees_per_account(account_id):
    # from consignee_account_mapping table
    try:

        conn = get_db_connection()

        if whichdb == 'mysql' and conn.is_connected():
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

            cursor.execute("select consigneeId, consigneeName, consigneeEmail FROM consignee_account_mapping WHERE "
                           "subAccountUCN = %s",
                           (account_id,))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

        else:
            cursor = conn.cursor()
            cursor1 = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
            # print("Changing issue date " + new_issue_date)
            cursor.execute(
                "select consigneeId, consigneeFirstName,consigneeLastName, consigneeEmail FROM consignee_account_mapping WHERE "
                "subAccountUCN = ?", (account_id,))
            # print("changed for " + str(notification_id))
            # gets the number of rows affected by the command executed
            output = cursor.fetchall()
            return output

    except Error as e:
        print("Error while connecting to MySQL", e)
