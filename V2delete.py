import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import urllib.request
import sqlite3
import time

#cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN
 
url='http://192.168.94.90/'#PUT HERE THE IP ADDRESS
cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
 
prev=""
pres=""

conn = sqlite3.connect('shopping_list.db')
cursor = conn.cursor()

# Drop the table if it exists
cursor.execute('DROP TABLE IF EXISTS shopping_list')

# Create a table for the shopping list
cursor.execute('''
CREATE TABLE shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    price REAL NOT NULL
)
''')
conn.commit()

def add_item(item, price):
    cursor.execute('INSERT INTO shopping_list (item, price) VALUES (?, ?)', (item, price))
    conn.commit()
    print(f'Added {item} with price ${price:.2f}.')

def delete_item(item):
    cursor.execute('DELETE FROM shopping_list WHERE item = ?', (item,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f'Item "{item}" not found.')
    else:
        print(f'Deleted item: {item}.')

def view_list():
    cursor.execute('SELECT item, price FROM shopping_list')
    rows = cursor.fetchall()
    if not rows:
        print('The shopping list is empty.')
    else:
        print('Shopping List:')
        for row in rows:
            print(f'Item: {row[0]}, Price: ${row[1]:.2f}')

def calculate_total():
    cursor.execute('SELECT SUM(price) FROM shopping_list')
    total = cursor.fetchone()[0]
    if total is None:
        total = 0.0
    print(f'Total cost of items: ${total:.2f}')

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
            x=str(obj.data)
            add_item(obj.data[:4], int(obj.data[5:]))
            view_list()
            cv2.putText(frame, str(WAIT), (50, 50), font, 2,(0, 0, 255), 3)
            time.sleep(.5)
            y=str(obj.data)
            if x==y:
                delete_item(obj.data[:4], int(obj.data[5:]))
                view_list()
            prev=pres
            
        cv2.putText(frame, str(obj.data), (50, 50), font, 2,(0, 0, 255), 3)
 
    cv2.imshow("live transmission", frame)
 
    key = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        view_list()
        total = calculate_total()
        print(f'Total cost: ${total:.2f}')
        conn.close()
        break
 
cv2.destroyAllWindows()
