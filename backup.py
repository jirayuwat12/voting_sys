import pyrebase
import json
import secret as sc

firebase = pyrebase.initialize_app(sc.config).database( )
 
def backup():
    data = firebase.get().val()
    with open('backup.json','w') as j:
        json.dump(data,j,indent=4)

if __name__ == "__main__":
    backup()