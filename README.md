# smart-meter-logger
Getting power usage data of ISKRA MT175 smart meter using python and a raspberry pi

- Show live data on simple Web Interface
- Write data to MySql Database
- Log Data into a csv File
- Code Should work with almost every smart meter with SML Version 1

The smart meter sends periodically data in the SML (Smart Message Language) Format. No communication to the smart meter is required.

## Example Web Interface Data
```
Electricity meter reading: 12339.7159 kWh
Overall Consumption: 665 W
Power Consumption Phase 1: 196 W
Power Consumption Phase 2: 308 W
Power Consumption Phase 3: 160 W
```

## SML Interpreation
```Hex Bytes``` Explanation from Smart Message Language Version 1 
```
1B 1B 1B 1B - escape sequence
``` 
```
01 01 01 01 - using protocol Version 1
``` 
In my case there are 3 SML Messages sent. Each Message got a "SML_MessageBody" which contains data specified below.  
Examples:  

## First SML Message:
```
760508a5345b62006200726301017601010502e1bc1f0bXXXXXXXXXXXXXXXXXXXX010163643200
```
A = 7x = List with x entries  
62 -> Unsigned8  
63 -> Unsigned16  
65 -> Unsigned32  
```
SML_Message
A  1          2    3    4                                                  5      6  
76 0508a401fb 6200 6200 726301017601010502e155ff0bXXXXXXXXXXXXXXXXXXXX0101 63b98e 00
SML_MessageBody (= 4 from SML_Message)
A  1      2  
72 630101 7601010502e155ff0bXXXXXXXXXXXXXXXXXXXX0101
SML_PublicOpen.Res (= 2 from SML_MessageBody - identfied by 1 = 0101)
A  1  2  3          4                       5  6
76 01 01 0502e155ff 0b XXXXXXXXXXXXXXXXXXXX 01 01
```

SML_Message  
{  
 1= transactionId Octet String,  
 2= groupNo 62->Unsigned8,  
 3= abortOnError 62->Unsigned8,  
 4= messageBody SML_MessageBody,  
 5= crc16 63->Unsigned16, (CRC16 DIN EN 62056-46)  
 6= endOfSmlMsg EndOfSmlMsg  
}
  
SML_MessageBody  
{  
 1 = OpenRequest [0x00000100] 2 = SML_PublicOpen.Req  
 1 = OpenResponse [0x00000101] 2 = SML_PublicOpen.Res  
 1 = CloseRequest [0x00000200] 2 = SML_PublicClose.Req  
 1 = CloseResponse [0x00000201] 2 = SML_PublicClose.Res  
 1 = GetProfilePackRequest [0x00000300] 2 = SML_GetProfilePack.Req  
 1 = GetProfilePackResponse [0x00000301] 2 = SML_GetProfilePack.Res  
 1 = GetProfileListRequest [0x00000400] 2 = SML_GetProfileList.Req  
 1 = GetProfileListResponse [0x00000401] 2 = SML_GetProfileList.Res  
 1 = GetProcParameterRequest [0x00000500] 2 = SML_GetProcParameter.Req  
 1 = GetProcParameterResponse [0x00000501] 2 = SML_GetProcParameter.Res  
 1 = SetProcParameterRequest [0x00000600] 2 = SML_SetProcParameter.Req  
 1 = SetProcParameterResponse [0x00000601] 2 = SML_SetProcParameter.Res  
 1 = GetListRequest [0x00000700] 2 = SML_GetList.Req  
 1 = GetListResponse [0x00000701] 2 = SML_GetList.Res  
 1 = AttentionResponse [0x0000FF01] 2 = SML_Attention.Res  
}  

SML_PublicOpen.Res 
{  
 1= codepage Octet String OPTIONAL (->01),  
 2= clientId Octet String OPTIONAL (->01),  
 3= reqFileId Octet String,  
 4= serverId Octet String,  
 5= refTime SML_Time OPTIONAL (->01),  
 6= sml-Version Unsigned8 OPTIONAL (->01),  
}  

## Second SML_Message (with interesting data)  
```
760508a5345c620062007263070177010bXXXXXXXXXXXXXXXXXXXX070100620affff7262016503fd4b6b7a77078181c78203ff010101010449534b0177070100000009ff010101010bXXXXXXXXXXXXXXXXXXXX0177070100010800ff650000018201621e52ff5900000000075bc3620177070100010801ff0101621e52ff5900000000075bc3620177070100010802ff0101621e52ff5900000000000000000177070100100700ff0101621b520055000001c00177070100240700ff0101621b520055000000cb0177070100380700ff0101621b5200550000005901770701004c0700ff0101621b5200550000009b0177078181c78205ff010101018302XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX010101630d9500
```
SML_GetList.Res Layout:  
{  
 1= clientId Octet String OPTIONAL (->01),  
 2= serverId Octet String,  
 3= listName Octet String OPTIONAL (->01),  
 4= actSensorTime SML_Time OPTIONAL (->01),  
 5= valList SML_List,  
 6= listSignature SML_Signature OPTIONAL (->01),  
 7= actGatewayTime SML_Time OPTIONAL (->01)  
} 

SML_Time ::= CHOICE
{
 1 = secIndex [0x01] Unsigned32,
 1 = timestamp [0x02] SML_Timestamp  (Unsigned32)
}

SML_List  
{  
 1 = valListEntry SML_ListEntry  
}  

SML_ListEntry  
{  
 1= objName Octet String,  
 2= status SML_Status OPTIONAL (->01),  
 3= valTime SML_Time OPTIONAL (->01),  
 4= unit SML_Unit -> DLMS Unit List OPTIONAL (->01),  
 5= scaler Integer8 OPTIONAL (->01),  
 6= value SML_Value,  
 7= valueSignature SML_Signature OPTIONAL (->01)  
}  
```
SML_Message
A  1          2    3    4              5      6 
76 0508a5345c 6200 6200 7263....010101 630d95 00
SML_MessageBody (= 4 from SML_Message)
A  1      2 
72 630701 7701...9500
SML_GetList.Res (= 2 from SML_MessageBody - identfied by 1 = 0701)
A  1  2                      3              4                  5          6  7
77 01 0bXXXXXXXXXXXXXXXXXXXX 070100620affff 7262016503fd4b6b 7a77....01 01 01
SML_Time (= 4 from SML_GetList.Res)
A  1    2
72 6201 6503fd4b6b
SML_List (= 5 from SML_GetList.Res)
A  1       2       3       4       5       6       7       8       9       10
7a 77...01 77...01 77...01 77...01 77...01 77...01 77...01 77...01 77...01 77...01 

SML_ListEntry 1:
A  1              2  3  4  5  6        7
77 078181c78203ff 01 01 01 01 0449534b 01
--> 1 = OBIS Code: 129-129:199.130.03*255 --> 6 = Value: ISK
SML_ListEntry 2:
A  1              2  3  4  5  6                      7
77 070100000009ff 01 01 01 01 0bXXXXXXXXXXXXXXXXXXXX 01
--> 1 = OBIS Code: 1-0:0.0.9*255 --> 6 = Value: Server ID
SML_ListEntry 3:
A  1              2          3  4    5    6                  7
77 070100010800ff 6500000182 01 621e 52ff 5900000000075bc362 01
--> 1 = OBIS Code: 1-0:1.8.0*255, 4 = Unit: Wh, 5 = scaler (int8) -1 = *10^-1 = /10, 6 = Value:  (int64) 123454306
SML_ListEntry 4:
A  1              2  3  4    5    6                  7
77 070100010801ff 01 01 621e 52ff 5900000000075bc362 01
--> 1 = OBIS Code: 1-0:1.8.1*255, 4 = Unit: Wh, 5 = scaler (int8) -1 = *10^-1 = /10, 6 = Value: (int64) 123454306
SML_ListEntry 5:
A  1              2  3  4    5    6                  7
77 070100010802ff 01 01 621e 52ff 590000000000000000 01
--> 1 = OBIS Code: 1-0:1.8.2*255, 4 = Unit: Wh, 5 = scaler (int8) -1 = *10^-1 = /10, 6 = Value: (int64) 0 
SML_ListEntry 6:
A  1              2  3  4    5    6          7
77 070100100700ff 01 01 621b 5200 55000001c0 01
--> 1 = OBIS Code: 1-0:16.7.0*255., 4 = Unit: W,  5 = 0, 6 = Value: (int32) 448
SML_ListEntry 7:
A  1              2  3  4    5    6          7
77 070100240700ff 01 01 621b 5200 55000000cb 01
--> 1 = OBIS Code: 1-0:36.7.0*255, 4 = Unit: W,  5 = 0, 6 = Value: (int32) 203
SML_ListEntry 8:
A  1              2  3  4    5    6          7
77 070100380700ff 01 01 621b 5200 5500000059 01
--> 1 = OBIS Code: 1-0:56.7.0*255, 4 = Unit: W,  5 = 0, 6 = Value: (int32) 89 
SML_ListEntry 9:
A  1              2  3  4    5    6          7
77 0701004c0700ff 01 01 621b 5200 550000009b 01
--> 1 = OBIS Code: 1-0:76.7.0*255, 4 = Unit: W,  5 = 0, 6 = Value: (int32) 155 
SML_ListEntry 10:
A  1              2  3  4  5  6                                                                                                    7
77 078181c78205ff 01 01 01 01 8302XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 01
--> 1 = OBIS Code: 129-129:199.130.5*255 --> 6 = Value: Public Key
```

  
## Third SML Message:
```
760508a5345d620062007263020171016353a700
```
Close-Message (SML_MessageBody = SML_PublicClose.Req = 0x0201)  
SML_PublicClose.Req Layout:  
{  
 1= globalSignature SML_Signature OPTIONAL (->01)  
}  
```
SML_Message
A  1          2    3    4            5      6 
76 0508a5345d 6200 6200 726302017101 6353a7 00
SML_MessageBody (= 4 from SML_Message)
A  1      2  
72 630201 7101
SML_PublicClose.Req (= 2 from SML_MessageBody - identfied by 1 = 0201)
A  1
71 01
--> no Signature
```

```
1B 1B 1B 1B - escape sequence
``` 
```
1a XX YY ZZ - end of message
``` 
```XX``` = number of padding bytes at the end of the message to get length division by 4  
```YY ZZ``` = Checksum - YY = MSB, ZZ = LSB

## Howto
### Connect to Smart Meter
For a connection to the Smart meter you need a USB infrared adapter. There are several adapters on the market that just need to be pluged in. They are usually detected as a casual serial port  ```(/dev/ttyUSB0)``` 

### Start
Download the files to a directory and start with ```sudo python sml.py```

### Watch live data
Enter the ip adress of your raspberry pi in your webbrowser.
Make sure no other program on the raspberry pi is using Port 80 (like another Webserver) 

### Autostart
edit /etc/rc.local and add:
```
cd /your/path
python sml.py 
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
