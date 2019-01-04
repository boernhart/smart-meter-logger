#!/usr/bin/python
from flask import Flask, jsonify, render_template
from threading import Thread
import sys
import serial
import time

db_active = True

start = '1b1b1b1b01010101' 
end = '1b1b1b1b1a'

p_L1 = 0
p_L2 = 0
p_L3 = 0
p_sum = 0
e_sum = 0

running = True
queue = []

app = Flask(__name__, template_folder='.')

@app.route('/')
def web_root():
    return render_template('index.html') 
    
@app.route('/website.js')
def ws():
    return render_template('website.js')

@app.route('/state')
def web_state():
    return jsonify(
        {
            'p_L1': str(getP_L1()),
            'p_L2': str(getP_L2()),
            'p_L3': str(getP_L3()),
            'p_sum': str(getP_sum()),
            'e_sum': str(getE_sum())
        })


def read_thread():
    data = ''
    buffer = ""
    count = 100

    port = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    global p_L1
    global p_L2
    global p_L3
    global p_sum
    global e_sum

    while running == True:
        if len(queue) > 0:
            queue.pop()()
        char = port.read()
        data = data + char.encode('HEX')
        pos = data.find(start)
        if (pos <> -1):
            data = data[pos:len(data)]
        pos = data.find(end)

        if (pos <> -1):
            data = data[0:pos + 10]

            search = '070100010800ff'  # Energy kWh
            pos = data.find(search)
            if (pos <> -1):
                pos = pos + len(search) + 22
                value = data[pos:pos + 16]
                e_sum = int(value, 16) / 1e4

            search = '070100100700ff'  # Sum Power L1,L2,L3
            pos = data.find(search)
            if (pos <> -1):
                pos = pos + len(search) + 14
                value = data[pos:pos + 8]
                p_sum = int(value, 16)

            search = '070100240700ff'  # current Power L1
            pos = data.find(search)
            if (pos <> -1):
                pos = pos + len(search) + 14
                value = data[pos:pos + 8]
                p_L1 = int(value, 16)

            search = '070100380700ff'  # current Power L2
            pos = data.find(search)
            if (pos <> -1):
                pos = pos + len(search) + 14
                value = data[pos:pos + 8]
                p_L2 = int(value, 16)

            search = '0701004c0700ff'  # current Power L3
            pos = data.find(search)
            if (pos <> -1):
                pos = pos + len(search) + 14
                value = data[pos:pos + 8]
                p_L3 = int(value, 16)

            if p_L1 < 4000000000 and p_L2 < 4000000000 and p_L3 < 4000000000 and e_sum < 400000 and e_sum > 0:  # Check if valid data
                buffer += str(time.strftime("%Y-%m-%d") + ' ' + time.strftime("%H:%M:%S") + ',' + str(e_sum) + ',' + str(
                    p_sum) + ',' + str(p_L1) + ',' + str(p_L2) + ',' + str(p_L3) + '\n')


                if count < 1:
                    count = 100
                    file = open('data.csv', 'a')
                    file.write(buffer)
                    file.close()
                    buffer = ""
                else:
                    count -= 1

                if db_active == True:
                    try:
                        cur.execute("INSERT INTO `smart_meter`.`values` (`time`, `e_sum`, `p_sum`, `p_L1`, `p_L2`, `p_L3`) VALUES (CURRENT_TIMESTAMP, " + str(e_sum) + ", " + str(p_sum) + ", " + str(p_L1) + ", " + str(p_L2) + ", " + str(p_L3) + ");")
                        db.commit()
                    except:
                        db.rollback()
                    
            data = ''

def stop_thread():
    running = False


def getP_L1():
    return p_L1


def getP_L2():
    return p_L2


def getP_L3():
    return p_L3


def getP_sum():
    return p_sum


def getE_sum():
    return e_sum
    

if __name__ == '__main__':
    global db
    global cur
    if db_active == True:
        import MySQLdb
    
        db = MySQLdb.connect(host="localhost",
                            user="admin",
                            passwd="root",
                            db="smart_meter")

        cur = db.cursor()

    t = Thread(target=read_thread)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=80)

