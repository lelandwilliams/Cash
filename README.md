# Cash - a personal finance management program

This program will process XML files that you download from your bank or credit card website, and database them. You can then assign them to categories, and the program will create reports about how much you have spent in those categories, and compare that across months.

I looked into the protocols for downloading the data directly from providers, but it would be a lot of work to implement, so it was easier just to use a pre-existing service.

## Usage:
if you run the ddl.py file, it will setup the database for mysql/mariadb. Just edit the file 
with the correct database username and password.

Put your downloaded transation files in a subdirectory called 'Files.'

The run driver.py, and it creates an instance of the class defined in money.py, and offers a text based dialog ('CUI').

