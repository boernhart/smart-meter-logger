#!/usr/bin/python
from flask import Flask, jsonify, render_template
from threading import Thread
import sys
import serial
import time

db_active = False

p_L1 = 0
p_L2 = 0
p_L3 = 0
p_sum = 0
e_sum = 0

running = True

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
            'p_L1': str(p_L1),
            'p_L2': str(p_L2),
            'p_L3': str(p_L3),
            'p_sum': str(p_sum),
            'e_sum': str(e_sum)
        })


def read_thread():
    data = ''
    buffer = ""
    count = 100

    # serial Port 9600 Baud, 8N1
    port = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    global p_L1
    global p_L2
    global p_L3
    global p_sum
    global e_sum

    while running == True:
        input = port.read()
        data = data + input.encode('HEX')

        pos = data.find('1b1b1b1b01010101')        # find start of Frame

        if (pos <> -1):
            data = data[pos:]                      # cut trash before start delimiter

        pos = data.find('1b1b1b1b1a')              # find end of Frame

        if (pos <> -1) and len(data) >= pos + 16:
            data = data[0:pos + 16]                # cut trash after end delimiter

         #   print(time.strftime("%H:%M:%S") + " : " + data)
         #   print("Padding Bytes: " + (data[-6:-5]))
         #   print("Checksum: " + (data[-4:]))
            
            pos = data.find('070100010800ff') # looking for OBIS Code: 1-0:1.8.0*255 - Energy kWh
            if (pos <> -1):
                e_sum = int(data[pos+36:pos + 52], 16) / 1e4

            pos = data.find('070100100700ff') # looking for OBIS Code: 1-0:16.7.0*255 - Sum Power L1,L2,L3
            if (pos <> -1):
                p_sum = int(data[pos+28:pos+36], 16)

            pos = data.find('070100240700ff') # looking for OBIS Code: 1-0:36.7.0*255 - current Power L1
            if (pos <> -1):
                p_L1 = int(data[pos+28:pos+36], 16)

            pos = data.find('070100380700ff') # looking for OBIS Code: 1-0:56.7.0*255 - current Power L2
            if (pos <> -1):
                p_L2 = int(data[pos+28:pos+36], 16)

            pos = data.find('0701004c0700ff') # looking for OBIS Code: 1-0:76.7.0*255 - current Power L3
            if (pos <> -1):
                p_L3 = int(data[pos+28:pos+36], 16)

            if p_L1 < 4000000000 and p_L2 < 4000000000 and p_L3 < 4000000000 and e_sum < 400000 and e_sum > 0:  # Check for valid data
                buffer += str(time.strftime("%Y-%m-%d") + ' ' + time.strftime("%H:%M:%S") + ',' + str(e_sum) + ',' + str(p_sum) + ',' + str(p_L1) + ',' + str(p_L2) + ',' + str(p_L3) + '\n')

                if count < 1: # only to reduce write accesses to SD Card
                    count = 100
                    file = open('data.csv', 'a')
                    file.write(buffer)
                    file.close()
                    buffer = ""
                else:
                    count -= 1

                if db_active == True:
                    try:
                        cur.execute(
                            "INSERT INTO `smart_meter`.`values` (`time`, `e_sum`, `p_sum`, `p_L1`, `p_L2`, `p_L3`) VALUES (CURRENT_TIMESTAMP, " + str(
                                e_sum) + ", " + str(p_sum) + ", " + str(p_L1) + ", " + str(p_L2) + ", " + str(
                                p_L3) + ");")
                        db.commit()
                    except:
                        db.rollback()

            data = ''


def stop_thread():
    running = False

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

