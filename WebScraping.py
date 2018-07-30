from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import sqlite3
import time

conn = sqlite3.connect("Nursing.sqlite")
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS Disease (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE,
    link TEXT UNIQUE,
    found INTEGER
);

CREATE TABLE IF NOT EXISTS Symptom (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT   
);

CREATE TABLE IF NOT EXISTS Checker (
    disease_id TEXT,
    symptom_id TEXT,
    PRIMARY KEY (disease_id , symptom_id)
);
""")

url = urllib.request.urlopen("https://www.everydayhealth.com/conditions/")
soup = BeautifulSoup(url, 'html.parser')

contents = soup.find("div", class_="col-xs-12 link-holder")
contents_soup = BeautifulSoup(contents.encode(), 'html.parser')
l = contents_soup.find_all("li")

for x in l:
    x_soup = BeautifulSoup(x.encode(), 'html.parser')
    try:
        disease_name = x_soup.a.string
        link_of_disease = x_soup.a.get("href")[2:]

        print("Disease name",disease_name ,"Link:" ,link_of_disease)
        cur.execute("INSERT OR REPLACE INTO Disease (name , link) VALUES (?, ?)",(disease_name,link_of_disease))

    except:
        pass

conn.commit()

disease_name = cur.execute("SELECT Disease.name , Disease.link FROM Disease ORDER BY Disease.name")

table = cur.fetchall()

for disease in table:
    print("disease :", disease)
    print("COLLECTING DATA FOR", disease[0])
    url = urllib.request.urlopen("https://" + disease[1])
    soup = BeautifulSoup(url, 'html.parser')

    # get all h2 from page
    list_of_h2 = []
    l = []
    for head in soup.find_all("h2"):
        # print(head)
        # print("try", head.find_next("ul") )
        soup = BeautifulSoup(head.encode(), 'html.parser')
        h2_find = soup.h2.string
        if "Symptoms" not in str(h2_find):
            continue
        # list_of_h2.append(str(h2_find))
        print("try2", head.find_next("ul"))

        soup = BeautifulSoup(head.find_next("ul").encode(), 'html.parser')
        l = soup.find_all('li')
    print("test", l)
    try:
        string_result = str(l[0])
        print(string_result)
        str1 = string_result.replace("<li>", ",")
        str2 = str1.replace("</li>", ",")
        print(str2)
        li = str2.split(",")
        print(li)
        for sys in li:
            if sys == "":
                continue
            cur.execute("INSERT OR REPLACE INTO Symptom (name) VALUES (?)",(sys,))
            cur.execute("SELECT id FROM Symptom WHERE name  = ?",(sys,))
            symptom_id = cur.fetchone()[0]

            cur.execute("SELECT id FROM Disease WHERE name  = ?", (disease[0],))
            nameofdisease = cur.fetchone()[0]

            cur.execute("INSERT OR REPLACE INTO Checker ( disease_id , symptom_id ) VALUES (?, ?)",(nameofdisease,symptom_id))


        conn.commit()
    except:
        pass




