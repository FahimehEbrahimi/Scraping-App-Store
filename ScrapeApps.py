import sqlite3
from sqlite3 import Error
import requests
from bs4 import BeautifulSoup

logfile = open("logfile.txt", "a+")

def create_connection():
    db_file ="Education.db"
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print('HERE')
        print(e)
        return


def create_tables(conn):
    sql_create_applications_table = """ CREATE TABLE IF NOT EXISTS applications (
                                                id integer PRIMARY KEY,
                                                appID integer NOT NULL UNIQUE ,
                                                name text NOT NULL,
                                                category text,
                                                description text,
                                                isFree integer,
                                                rating real,
                                                ratingCount text
                                            ); """

    # create applications table
    create_table(conn, sql_create_applications_table)


def create_app(conn, app):
    sql = ''' INSERT INTO applications(appId, name, category, description, isFree, rating, ratingCount)
                  VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, app)
    return cur.lastrowid



def getDescription(soup, id):
    desc = []
    try:
        descriptionDiv = soup.find('div', {'class' : 'section__description'})
        descriptionP = descriptionDiv.find_all('p')

        for p in descriptionP:
            desc.append(p.text)
            desc.append(" \n ")
        return desc[0]
    except Exception as e:
        logfile.write("getDescription: id= " + id + str(e) + "\n")
        return ""

def replace_with_newlines(element, id):
    try:
        text = ''
        for elem in element.recursiveChildGenerator():
            if elem.name == 'br':
                text += '\n'
            else:
                text += elem.strip()
        return text
    except Exception as e:
        logfile.write("replace_with_newlines: id= " + id + str(e) + "\n")
        return element

def getDescription2(soup, id):
    desc = []
    try:
        descriptionDiv = soup.find('div', {'class' : 'section__description'})
        descriptionP = descriptionDiv.find_all('p')

        for p in descriptionP:
            line = replace_with_newlines(p, id)
            desc.append(line)
        return desc
    except Exception as e:
        logfile.write("getDescription2: id= " + id + str(e) + "\n")
        return ""

def getName(soup, id):
    try:
        titleHeader = soup.find('h1', {'class' : 'product-header__title'})
        return titleHeader.text.split("\n")[1].lstrip().rstrip()
    except Exception as e:
        logfile.write("getName: id= " + id + str(e) + "\n")
        return ""

def getRatingAvg(soup, id):
    try:
        ratingText = soup.find('figcaption', {'class': 'we-rating-count'}).text
        return ratingText.split(',')[0]
    except Exception as e:
        logfile.write("getRatingAvg: id= " + id + str(e) + "\n")
        return 0

def getRatingCount(soup, id):
    try:
        ratingText = soup.find('figcaption', {'class': 'we-rating-count'}).text
        return (ratingText.split(',')[1]).lstrip().split(' ')[0]
    except Exception as e:
        logfile.write("getRatingCount: id= " + id + str(e) + "\n")
        return ""

def getPrice(soup, id):
    try:
        return soup.find('li', {'class': 'app-header__list__item--price'}).text
    except Exception as e:
        logfile.write("getPrice: id= " + id + str(e) + "\n")
        return ""

def getInAppPurchaseInfo(soup, id):
    try:
        soup.find('li', {'class': 'app-header__list__item--in-app-purchase'}).text
        return True
    except Exception as e:
        logfile.write("getInAppPurchaseInfo: id= " + id + str(e) + "\n")
        return False

def isAppFree(soup, id):
    try:
        if getPrice(soup, id) == "Free":
            if getInAppPurchaseInfo(soup, id):
                return 2 # In app purchases
            else:
                return 0 # totally free
        else:
            return 1 #non-free
    except Exception as e:
        logfile.write("isAppFree: id= "+ id + str(e)+ "\n")
        return -1


def main():
    # create a database connection
    #print(-1)
    conn = create_connection()
    #print(-2)
    IDs = []
    with open('educationOut.txt') as f:
        IDs = f.read().splitlines()
    if conn:
        create_tables(conn)
        for id in IDs:
            print(IDs.index(id))
            try:
                url = requests.get("https://apps.apple.com/us/app/id" + str(id))
                html = url.text
                soup = BeautifulSoup(html, 'html.parser')

                if getName(soup, id) != "":
                    # ID, name, category, desc, isFree, rating, ratingCount
                    app = (id, getName(soup, id), 'Education', getDescription2(soup, id)[0], isAppFree(soup, id), getRatingAvg(soup, id), getRatingCount(soup, id))
                    create_app(conn, app)
                    conn.commit()
            except Exception as e:
                logfile.write(str(e) + "\n")

        conn.close()



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logfile.write('Error in Scraping: ' + str(e) + "\n")
    logfile.close()