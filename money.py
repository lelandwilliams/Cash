#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import mysql.connector
import os
import csv

class Budget():
    def __init__(self):
        self.home_directory = os.getcwd()
        self.dialog_and_process = False

        config = {
                'password':'cashmoney',
                'user':'python',
                'database':'cash'
                }
        self.sql = mysql.connector.connect(**config)
        
    def category_varies_exists(self):
        cur = self.sql.cursor()
        cur.execute("SELECT COUNT(*) FROM vendor WHERE category = 'Varies'")
        result = cur.fetchone()[0]
        cur.close()
        return result > 0

    def create_budget_columns(self):
        cur = self.sql.cursor()
        columns = []
        cur.execute('SELECT DISTINCT category FROM vendor')
        for col in cur.fetchall():
            cur.execute('ALTER TABLE budget ADD `' + col[0] + '` DECIMAL(7,2) DEFAULT 0.00')
        cur.close()

    def create_budget_row(self, date):
        cur = self.sql.cursor()

        query = ("SELECT COUNT(*) FROM budget WHERE month = MONTH(%s) AND year = YEAR(%s)")
        cur.execute(query, (date, date))
        result = cur.fetchone()[0]
        if result == 0:
            cur.execute("INSERT INTO budget (month,year) VALUES(MONTH(%s),YEAR(%s))", (date ,date))
        else:
            pass

        self.sql.commit()
        cur.close()

    def create_vendor(self, v):
        cur = self.sql.cursor()
        query = ('SELECT COUNT(*) FROM vendor WHERE name = "' + v +'"')
        cur.execute(query)
        result = cur.fetchone()[0]
        if result == 0:
            cur.execute("INSERT INTO vendor VALUES(%s,%s,%s)", (v,v,v))
            query = ("ALTER TABLE budget ADD `" + v + "` DECIMAL(7,2) DEFAULT 0.00")
            cur.execute(query)
        self.sql.commit()
        cur.close()

    def get_aliases(self):
        cur = self.sql.cursor()
        cur.execute("SELECT DISTINCT alias FROM vendor WHERE name != alias") 
        alist = []
        for i in cur:
            alist.append(i[0])
        cur.close()
        return alist

    def get_alias_and_category(self, vendor):
        cur = self.sql.cursor()
        query = ('SELECT alias, category FROM vendor where name = "' + vendor + '"')
        cur.execute(query)
        result = cur.fetchone()
        cur.close()
        alias = result[0]
        category = result[1]

        return alias,category

    def get_indexes(self):
        cur = self.sql.cursor()
        cur.execute('SELECT idx FROM transaction')
        indexes = []
        for i in cur:
            indexes.append(i[0])
        cur.close()
        return indexes

    def get_transactions_by_vendor(self,vendor):
        cur = self.sql.cursor()
        cur.execute('SELECT vendor, date, amount FROM transaction where vendor = "' +
            vendor + '"')
        result = cur.fetchall()
        cur.close()
        return result

    def get_vendor_category(self):
        cur = self.sql.cursor()
        cur.execute("SELECT DISTINCT category FROM vendor WHERE name != category")
        name_list = []
        for i in cur:
            name_list.append(i[0])
        cur.close()
        name_list.sort()
        return name_list

    def get_vendor_same_name_and_category(self):
        cur = self.sql.cursor()
        query = ("SELECT name FROM vendor WHERE name = category OR name = alias")
        cur.execute(query)
        name_list = []
        for i in cur:
            name_list.append(i[0])
        cur.close()
        return name_list

    def insert_transaction(self,date,amount,vendor,alias,category):
            cur = self.sql.cursor()
            cur.execute("INSERT INTO transaction VALUES(%s,%s,%s,%s,%s,%s)",
                    ('NULL', date, amount, vendor, alias, category))

            self.create_budget_row(date)

            query = ("UPDATE budget SET `" + category +"` = `" + category + "` + " + str(amount) +
                    "WHERE month = MONTH(%s) AND year = YEAR(%s)")
            cur.execute(query, (date,date))

            self.sql.commit()
            cur.close()

    def is_new_transaction(self,date,vendor,amount):
        cur = self.sql.cursor()
        cur.execute(
                "SELECT COUNT(*) FROM transaction WHERE date = %s AND amount = %s",
                (date,amount))
        val =( cur.fetchone()[0] == 0)
        cur.close()
        return val

    def process_directory(self):
        files = os.listdir('files')
        os.chdir('files')
        for f in files:
            self.process_csv(f)
#           print(f)
        self.refresh_categories()

    def process_csv(self,filename):
        f_obj = open(filename, 'r')
        reader = csv.DictReader(f_obj)

        if reader.fieldnames[1] == "Trans Date":
            self.source = 'Visa'
            self.date = 'Trans Date'
            self.vendor = 'Description'
        elif reader.fieldnames[1] == "Date":
            self.source = 'Google'
            self.date = 'Date'
            self.vendor = 'Place'
        else:
            self.date = 'Date'
            self.vendor = 'Name'
            self.source = 'US'

        for row in reader:
            self.process_row(row)

        f_obj.close()

    def process_date(self,s):
        parts = s.split('/')
        return (parts[2] + '-' + parts[0] + '-' + parts[1])

    def process_row(self, row):
            date = self.process_date(row[self.date])
            amount = float(row['Amount'].replace('$','').replace(',',''))
            vendor = row[self.vendor].strip()

            if self.is_new_transaction(date,vendor,amount):
                self.create_vendor(vendor)
                alias, category = self.get_alias_and_category(vendor)
                self.insert_transaction(date,amount,vendor,alias,category)

    def refresh_budget_category(self,category):
        cur = self.sql.cursor()
        cur.execute("SELECT DISTINCT month,year FROM budget")
        result = cur.fetchall()
        cur.close()
        for month,year in result:
            self.refresh_budget_category_row(category,month,year)

    def refresh_budget_category_row(self,category,month,year):
        cur = self.sql.cursor()
        
        query = ("UPDATE budget SET `")
        query += category
        query += ("` = (SELECT SUM(amount) FROM transaction WHERE MONTH(date) = %s AND YEAR(date) = %s AND category = %s) WHERE MONTH = %s AND YEAR = %s")
        cur.execute(query, (month,year,category,month,year))

        cur.execute("UPDATE budget SET `%s` = 0.00 WHERE `%s` IS NULL" %(category,category))
        self.sql.commit()
        cur.close()

    def refresh_categories(self):
        cur = self.sql.cursor()
        cur.execute("SELECT DISTINCT category FROM vendor")
        result = cur.fetchall()
        cur.close()
        for row in result:
            self.refresh_budget_category(row[0])

    def remove_duplicate_transactions(self):
        indexes = self.get_indexes()
        cur = self.sql.cursor()

        for index in indexes[:-1]:
            cur.execute('SELECT date,vendor,amount FROM transaction WHERE idx = ' + str(index))
            transaction = cur.fetchall()
            if len(transaction) == 1:
                transaction = transaction[0]

                for j in indexes[indexes.index(index) + 1:]:
                    cur.execute('SELECT date,vendor,amount FROM transaction WHERE idx = ' + str(j))
                    transaction1 = cur.fetchall()
                    if len(transaction1) == 1:
                        transaction1 = transaction1[0]
                        is_duplicate = True
                        for k in range(len(transaction)):
                            if transaction[k] != transaction1[k]:
                                is_duplicate = False
                        if is_duplicate:
                            cur.execute('DELETE FROM transaction WHERE idx = ' + str(j))
                            self.sql.commit()
        cur.close()


    def update_alias(self,name,newalias):
        cur = self.sql.cursor()
        query = ('SELECT * FROM vendor WHERE name = "' + name  + '"')
        cur.execute(query)
        result = cur.fetchone()
        if newalias != result[1]:
            query = ('UPDATE vendor SET alias = "' + newalias + '" WHERE name = "' + name+'"')
            cur.execute(query)
            query = ('UPDATE transaction SET alias = "' + newalias + '" WHERE vendor = "' + name+'"')
            cur.execute(query)

        self.sql.commit()
        cur.close()

    def update_vendor_category(self,name,newcategory):
        cur = self.sql.cursor()
        query = ('SELECT category FROM vendor WHERE name = "' + name  + '"')
        cur.execute(query)
        result = cur.fetchone()
        oldcategory = result[0]
        if newcategory != oldcategory:
            query = ('UPDATE vendor SET category = "' + newcategory + '" WHERE name = "' + name+'"')
            cur.execute(query)
            query = ('UPDATE transaction SET category = "' + newcategory + '" WHERE vendor = "' + name+'"')
            cur.execute(query)
            # See if now there exists more than one vendor with a  category of name 'newcategory'
            query = ("SELECT COUNT(*) FROM vendor WHERE category = '" + newcategory + "'" )
            cur.execute(query)
            if cur.fetchone()[0] > 1:
                #  if there are more than one, resum the new category
                self.refresh_budget_category(newcategory)
                
                # and then try to remove oldcategory as column from cash.budget
                # if no vendors have it as a category
                query = ('SELECT COUNT(*) FROM vendor WHERE category = "' + oldcategory + '"' )
                cur.execute(query)
                if cur.fetchone()[0] == 0:
                    query = ("ALTER TABLE budget DROP `" + oldcategory + "`" )
                    cur.execute(query)
            else:
                # otherwise just rename the category
                query = ("ALTER TABLE budget CHANGE `"+ oldcategory + "` `" + newcategory + "` DECIMAL(7,2) DEFAULT 0.00")
                cur.execute(query)

        self.sql.commit()
        cur.close()

    def update_table(self,month):
        pass

