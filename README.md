# smart-meter-logger
Getting power usage data of ISKRA MT175 smart meter using python and a raspberry pi

- Show live data on simple Web Interface
- Write data to MySql Database
- Log Data into a csv File

## Example Web Interface Data
```
Electricity meter reading: 12339.7159 kWh
Overall Consumption: 665 W
Power Consumption Phase 1: 196 W
Power Consumption Phase 2: 308 W
Power Consumption Phase 3: 160 W
```
## Howto
### Connect to Smart Meter
For a connection to the Smart meter you need a USB infrared adapter. There are several adapters on the market that just need to be pluged in. They are usually detected as a casual serial port  ```(/dev/ttyUSB0)``` 

### Start
Download the files to a directory and start with ```sudo python MyPower.py```

### Watch live data
Enter the ip adress of your raspberry pi in your webbrowser.
Make sure no other program on the raspberry pi is using Port 80 (like another Webserver) 

### Autostart
edit /etc/rc.local and add:
```
cd /your/path
python MyPower.py 
```

# For database support
```
sudo apt-get install python-mysqldb
```
## For local Database: 
Attention when using SD Card for Database - may damage the SD Card after a few Month/Years!

### Install MySQL Server
```
sudo apt-get install mysql-server
```

### Generate Database User
If first time no Password is set -> press Return when asked for password
```
pi@raspberrypi:~/ $ sudo mysql -u root -p
MariaDB [(none)]> create user admin@localhost identified by 'root';
Query OK, 0 rows affected (0.00 sec)
MariaDB [(none)]> grant all privileges on *.* to admin@localhost with grant option;
Query OK, 0 rows affected (0.00 sec)
MariaDB [(none)]> quit
Bye
```
### Generate Database Table
```
pi@raspberrypi:~/ $ sudo mysql -u admin -p 
MariaDB [(none)]> CREATE DATABASE smart_meter;
Query OK, 1 row affected (0.00 sec)
MariaDB [(none)]> USE smart_meter;
Database changed
MariaDB [(none)]> CREATE TABLE `values` (
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `e_sum` float DEFAULT NULL,
  `p_sum` int(11) DEFAULT NULL,
  `p_L1` int(11) DEFAULT NULL,
  `p_L2` int(11) DEFAULT NULL,
  `p_L3` int(11) DEFAULT NULL,
  KEY `time_IDX` (`time`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
Query OK, 0 rows affected (0.05 sec)
MariaDB [(none)]> quit
Bye
```

### Check Data in Database
```
sudo mysql -u admin -p 
MariaDB [(none)]> SELECT * FROM smart_meter.values;
```
```
+---------------------+---------+-------+------+------+------+
| time                | e_sum   | p_sum | p_L1 | p_L2 | p_L3 |
+---------------------+---------+-------+------+------+------+
| 2019-01-04 19:58:57 | 12338.7 |   382 |  199 |  160 |   23 |
| 2019-01-04 19:58:59 | 12338.7 |   392 |  207 |  161 |   23 |
| 2019-01-04 19:59:01 | 12338.7 |   428 |  241 |  163 |   22 |
| 2019-01-04 19:59:02 | 12338.7 |   376 |  191 |  162 |   22 |
| 2019-01-04 19:59:04 | 12338.7 |   433 |  248 |  161 |   23 |
| 2019-01-04 19:59:06 | 12338.7 |   378 |  194 |  160 |   23 |
| 2019-01-04 19:59:08 | 12338.7 |   382 |  199 |  159 |   24 |
| 2019-01-04 19:59:10 | 12338.7 |   410 |  223 |  164 |   24 |
| 2019-01-04 19:59:11 | 12338.7 |   390 |  198 |  169 |   21 |
| 2019-01-04 19:59:13 | 12338.7 |   388 |  199 |  164 |   24 |
| 2019-01-04 19:59:15 | 12338.7 |   408 |  223 |  162 |   22 |
....
```
