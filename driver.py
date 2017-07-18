# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import csv
import money

menus = {}
menus['Main Menu'] = {}
menus['Main Menu']['Read File Data'] = "budget.process_directory()"
menus['Main Menu']['Process Transaction Lines'] = "process_transactions()"
menus['Main Menu']['Reports'] = "reports()"

menus['Process Transaction Lines'] = {}
menus['Process Transaction Lines']['Re-Alias and Categorize New Vendors'] = "realias_and_categorize()"
menus['Process Transaction Lines']['Change Vendor Category'] = "change_vendor_category()"
menus['Process Transaction Lines']['Change Vendor Alias'] = "change_vendor_alias()"

menus['Update Vendor'] = {}
menus['Update Vendor']['Skip'] = ""
menus['Update Vendor']['View Transactions'] = ""
menus['Update Vendor']['Change Alias'] = ""
menus['Update Vendor']['Change Category'] = ""

menus['Reports'] = {}
menus['Reports']['Report'] = 'reports()'

budget = money.Budget()
cols = int(os.popen('stty size', 'r').read().split()[1])

def dialog(menu_type = 'Main Menu'):
    choice = -1
    while choice != 0:
        make_box_top(menu_type)

        i = 0
        if menu_type == 'Main Menu':
            choices = ['Quit']
        else:
            choices = ['Back']

        if (menu_type != 'Main Menu' and menu_type != 'Process Transaction Lines' and 
                menu_type != 'Update Vendor'):
            choices += ['Create New']

        a = (list(menus[menu_type].keys()))
        a.sort()
        choices += a

        width = 0
        for j in choices:
            if len(j) > width:
                width = len(j)

        if len(choices) > 18 and len(choices) <= 36 :
            for j in range(len(choices)//2):
               if (j*2) +1 > len(choices):
                    s = ("%i. " %(j)) + choices[j]
                    print(' *' + s.ljust(width + 3).center((cols - 4)) + '* ')
               else:
                   s1 = (("%i. " %(j)) + choices[j].ljust(width+3))
                   s2 = (("%i. " %(len(choices)//2 + j)) + choices[len(choices)//2 + j]).ljust(width +3)
                   print(' *' + (s1 + "     " + s2).center(cols -4) + '* ')
        elif len(choices) > 36:
            for j in range(len(choices)//3):
               if (j*3) +2 > len(choices):
                   s1 = (("%i. " %(j)) + choices[j].ljust(width+3))
                   s2 = (("%i. " %(len(choices)//3 + j)) + choices[len(choices)//3 + j]).ljust(width +3)
                   print(' *' + (s1 + "     " + s2).center(cols -4) + '* ')
               elif (j*3) + 1 > len(choices):
                    s = ("%i. " %(j)) + choices[j]
                    print(' *' + s.ljust(width + 3).center((cols - 4)) + '* ')
               else:
                   s1 = (("%i. " %(j)) + choices[j].ljust(width+3))
                   s2 = (("%i. " %(len(choices)//3 + j)) + choices[len(choices)//3 + j]).ljust(width +3)
                   s3 = (("%i. " %(2*len(choices)//3 + j)) + choices[2*len(choices)//3 + j]).ljust(width +3)
                   print(' *' + (s1 + "     " + s2 + "     " + s3).center(cols -4) + '* ')
        else:
            for j in choices :
                s = ("%i. " %(i)) + j
                print(' *' + s.ljust(width + 3).center((cols - 4)) + '* ')
                i += 1
        make_box_bottom()
        choice = input('  your choice --> '.center(cols).rstrip() + ' ')
        if not choice.isdecimal():
            choice = -1
            continue
        else:
            choice = int(choice)
        if choice != 0:
            if menu_type == 'Main Menu' or menu_type == 'Process Transaction Lines':
                eval(menus[menu_type][choices[choice]])
            else:
                return choices[choice]

def process_transactions():
    if budget.category_varies_exists():
        menus['Process Transaction Lines']['Process Varying Category Transactions'] = "process_varies()"
    dialog('Process Transaction Lines')

def change_vendor_alias(vendor = ''):
    if vendor == '':
        vendors = budget.get_vendors()
        vendor = choose_vendor(vendors)
    if vendor != 'Back':
        aliases = budget.get_aliases()
        menus['Change Alias'] = {}
        menus['Change Alias']['Create New'] = ''
        for a in aliases:
            menus['Change Alias'][a] = ''
        alias = dialog('Change Alias')
        if alias == 'Create New':
            alias = create_new(vendor, 'alias')
        if alias != 'Back':
            budget.update_alias(vendor,alias)
    
def change_vendor_category(vendor = ''):
    if vendor == '':
        vendors = budget.get_vendors()
        vendor = choose_vendor(vendors)
    if vendor != 'Back':
        menus['Change Vendor Category'] = {}
        menus['Change Vendor Category']['Create New']  = ''
        if not budget.category_varies_exists():
            menus['Change Vendor Category']['Varies'] = ''
        categories = budget.get_vendor_category()
        for c in categories:
            menus['Change Vendor Category'][c] = ''
        category = dialog('Change Vendor Category')
        if category == 'Create New':
            category = create_new(vendor, 'category')
        if category != 'Back':
            budget.update_vendor_category(vendor,category)

def choose_vendor(vendors):
    menus['Change Vendor Info'] = {}
    for name in vendors:
        menus['Change Vendor Info'][name] = ''
    vendor = dialog('Change Vendor Info')
    return vendor

def create_new(vendor, type_str):
    status = ''
    while status.lower() != 'y':
        new = input(('type in your new %s --> ' %(type_str)).center(cols).rstrip())
        while status.lower() != 'y' and status.lower() != 'n':
            status = input('are you happy with your new field (y/n) --> '.center(cols).rstrip())
    return new

def make_box_bottom():
    print(' *' + " " * (cols - 4) + "* ")
    print(' *' + " " * (cols - 4) + "* ")
    print(" " + "*" * (cols - 2) + " ")
    print()

def make_box_top(headline):
    print(" " + "*" * (cols - 2) + " ")
    print(' *' + " " * (cols - 4) + "* ")
    print(' *' + headline.center(cols - 4) + '* ')
    print(' *' + " " * (cols - 4) + "* ")
    print(' *' + " " * (cols - 4) + "* ")
    
def realias_and_categorize():
    vendors = budget.get_vendor_same_name_and_category()
    print()
    choice = ''
    for vendor in vendors:
        alias, category = budget.get_alias_and_category(vendor)
        if choice == 'Back':
            break
        os.system('clear')
        print(('---  %s  ---' %(vendor)).center(cols)) 
        print(alias.center(cols))
        print(category.center(cols))
        print()
        choice = dialog('Update Vendor')
        while choice != 'Back' and choice != 'Skip':
            if choice == 'Change Alias':
                change_vendor_alias(vendor)
            elif choice == 'Change Category':
                change_vendor_category(vendor)
            elif choice == 'View Transactions':
                transactions = budget.get_transactions_by_vendor(vendor)
                print()
                for trans in transactions:
                    print('%40s %10s $ %10s' %(trans[0],trans[1],trans[2]))
                print()
            if choice != 'View Transactions':
                os.system('clear')
            else:
                print()
            alias, category = budget.get_alias_and_category(vendor)
            print(('---  %s  ---' %(vendor)).center(cols)) 
            print(alias.center(cols))
            print(category.center(cols))
            print()
            choice = dialog('Update Vendor')




def reports():
    os.system('clear')
    month_3 = ['',"Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"]
    seperator = ' '
    sep = ' ' + seperator + ' '
    cat_line_sep = ''
#   cat_line_sep = '\n'
    categories = budget.get_vendor_category()
    data = {}
    year = 2014
    cur = budget.sql.cursor()
    data_length = 0

    cat_width = 0
    for category in categories:
        if len(category) > cat_width:
            cat_width = len(category)

    month_line = ' ' * cat_width + sep
    year_line = ' ' * cat_width + sep
    for month in range(13,18):
        mon = month
        if month > 12:
            mon = month - 12
            year = 2015
        month_line += month_3[mon].rjust(8) + sep
        year_line += str(year).rjust(8) + sep
    month_line += 'Averages'.rjust(8)

    print(month_line,'\n',year_line)

    for category in categories:
        data[category] = []
        for month in range(13,18): 
           mon = month
           if month > 12:
                year = 2015
                mon = month - 12
           else:
                year = 2014
           query = "SELECT `%s` FROM budget WHERE month = %i and year = %i" %(category,mon,year)
           cur.execute(query)
           data[category].append(cur.fetchone()[0])
        data[category].append(sum(data[category])/len(data[category]))

        cat_line = category.ljust(cat_width) + sep
        for amount in data[category]:
           cat_line += format(amount,'.2f').rjust(8) + sep
        print(cat_line,cat_line_sep)
        data_length = len(data[category])

    print()
    total_line = 'Total'.ljust(cat_width) + sep
    for i in range(data_length):
        total = 0
        for category in categories:
            total += data[category][i]
        total_line += format(total,'.2f').rjust(8) + sep
    print(total_line,'\n')

    whatever = input('Press Enter to continue'.center(cols))



dialog()
