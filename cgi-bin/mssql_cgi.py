#!/usr/bin/python
import pymssql
import time
import wtclib_mssql
import datetime
import socket
import ConfigParser

def get_a_mssql_cur_forever():
    while True:
        (ret, err)=wtclib_mssql.get_a_mssql_cur_once("conf.ini")
        if None != ret:
            return ret
        else:
            print (err)
            time.sleep(20)
class Mssql:
    def __Connect(self):
        self.conn = get_a_mssql_cur_forever()
        try:
            cur = self.conn.cursor()
        except Exception, e:
            print (str(e))
            return None
        return cur
    def select(self, sql):
        try:
            cur = self.__Connect()
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            self.conn.close()
            return rows
        except Exception, e:
            print (str(e))
            return ''
    def insert(self, sql):
        try:
            cur = self.__Connect()
            cur.execute(sql)
            cur.close()
            self.conn.commit()
            self.conn.close()
            return 0
        except Exception, e:
            print (str(e))
            return None
def get_a_users_config(conf_file):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(conf_file)
    except Exception, e:
        return None, str(e)+' db'
    secs = cf.sections()
    try:
        opts = cf.options("users")
    except Exception, e:
        return None, str(e)+' users'
    try:
        _refresh_sec = cf.getint("users", "refresh_sec")
        _all_device_min = cf.getint("users", "all_device_min")
        return _refresh_sec, _all_device_min
    except Exception, e:
        return None, str(e)+' get db'
(refresh, all_device) = get_a_users_config("conf.ini")
if None == refresh:
    refresh = 15
    all_device = 480
print "Content-type:text/html\n\n"
print """<html>
<head>
<meta content="text/html;charset=ISO-8869-1" http-equiv="content-type">
<meta http-equiv="refresh" content="%d" />
<title>New Device</title>
</head>
<body>
<h1>New Devices in %d min</h1>
<table>
	<tr>
<td width="200">CPUINFO</td><td width="250">time</td><td  width="200"> MAC</td><td width="120">cameraID</td><td width="200">Picture</td>
</tr>"""%(refresh, all_device)

mssql = Mssql()
_timeNow = datetime.datetime.fromtimestamp(time.time()-5*60)
#print _timeNow
_sql = "select * from dbo.IPNC where DeviceTypeID=430 and EditFlag>dateadd(minute,-%d,getdate())"%all_device
socket.setdefaulttimeout(1)
_devices = mssql.select(_sql)
#print time.time()
#_devices = None
print "device all=%d"%len(_devices)
if None != _devices:
    _devs = sorted(_devices, key=lambda x:x[5], reverse=True)
    for dev in _devs:
        _macStr = "%06X" % dev[5]
        _mac = "00-1B-38-%s-%s-%s" % (_macStr[0:2], _macStr[2:4], _macStr[4:6])
        _sql = "select * from dbo.hvpdOnline1 WHERE cameraID='%s'"%dev[0]
        _hvpd = mssql.select(_sql)
        if 0 == len(_hvpd):
            _alink = ''
        else:
            _ip = _hvpd[0][1].rstrip(' ')
            _alink = "<a href='http://%s/'>pic</a>"%_ip
        if dev[13] > _timeNow:
            print "<tr><td>%s</td> <td>%s</td> <td>%s</td> <td bgcolor=red>%s</td><td>%s</td></tr>"%(dev[7], dev[13],_mac,  dev[0], _alink)
        else:
            print "<tr><td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td><td>%s</td></tr>" % (dev[7], dev[13],_mac,  dev[0], _alink)
print """</table> </body> </html>"""



