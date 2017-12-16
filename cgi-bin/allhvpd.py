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

print "Content-type:text/html\n\n"
print """<html>
<head>
<meta content="text/html;charset=ISO-8869-1" http-equiv="content-type">
<meta http-equiv="refresh" content="10" />
<title>All Online HVPDS</title>
</head>
<body>
"""
_timeSecInt = int(time.time())
mssql = Mssql()
_sql = "select * from dbo.hvpdOnline1 where reNewTimet>%d"%(_timeSecInt-30)
socket.setdefaulttimeout(1)
_devices = mssql.select(_sql)
_len_hvpd = len(_devices)

if 0 != _len_hvpd:
    print "found %d HVPDS" % _len_hvpd
    print """<table><tr><td width="100">SN</td><td  width="100"> Images</td>
    <td  width="150"> IP</td><td  width="150">Status</td><td width="200">Connect Time</td></tr>"""
    for dev in _devices:
        _ip = dev[1].rstrip(' ')
        _alink = "<a href='http://%s/'>Picture</a>"%_ip
        _status_link = "<a href='http://%s/cgi-bin/status.cgi'>Status</a>"%_ip
        print "<tr><td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td><td>%s</td></tr>" % (dev[0], _alink,_ip,_status_link, dev[4])
    print "</table>"
print """ </body> </html>"""



