import cv2 # pip install opencv-python
import numpy as np # pip install numpy
import pyzbar.pyzbar as pyzbar # pip install pyzbar
import urllib.request
import sqlite3
 
#cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN
 
url='http://192.168.94.90/'#PUT HERE THE IP ADDRESS
cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
 
prev=""
pres=""

def create_table():
    conn = sqlite3.connect('shopping_list.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    DROP TABLE IF EXISTS shopping_list
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shopping_list (
        id INTEGER PRIMARY KEY,
        item_name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def add_item(item_name, price):
    conn = sqlite3.connect('shopping_list.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO shopping_list (item_name, price)
    VALUES (?, ?)
    ''', (item_name, price))
    
    conn.commit()
    conn.close()

def calculate_total():
    conn = sqlite3.connect('shopping_list.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT price FROM shopping_list')
    items = cursor.fetchall()
    
    total_cost = sum(price for (price,) in items)
    
    conn.close()
    return total_cost


while True:
    img_resp=urllib.request.urlopen(url+'cam-hi.jpg')
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    frame=cv2.imdecode(imgnp,-1)
    #_, frame = cap.read()
 
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        pres=obj.data
        if prev == pres:
            pass
        else:
            create_table()
            str(obj.data)
            print(obj.data[5:])
            add_item(obj.data[:4], int(obj.data[5:]))
            print("Items: ",obj.data[:4]," ","Price: ",int(obj.data[5:]))
            prev=pres
            
        cv2.putText(frame, (obj.data[:4],int(obj.data[5:])), (50, 50), font, 2,(0, 0, 255), 3)
 
    cv2.imshow("live transmission", frame)
 
    key = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        total = calculate_total()
        print(f'Total cost: ${total:.2f}')
        break
 
cv2.destroyAllWindows()
