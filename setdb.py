import pyrebase 

import json
import secret as sc
firebase = pyrebase.initialize_app(sc.config).database( )

def setzeroDB():
    with open('cpeng-voting-logo-default-rtdb-export.json') as j:
        data = json.load(j)
        firebase.set(data)

def setfrombackup():
    with open('backup.json') as j:
        data = json.load(j)
        firebase.set(data)


if __name__ == "__main__":
    setzeroDB()