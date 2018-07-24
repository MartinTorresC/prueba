'''
Created on Mar 5, 2018

@author: User1
'''
import telnetlib
import time
import socket
import datetime

try:
    
    tn= telnetlib.Telnet ('192.168.2.200',49152)
    time.sleep(2)
    msg = tn.read_very_eager()
    time.sleep(2)
    print repr(msg)
    
    time.sleep(2)
    msg = tn.read_very_eager()
    print msg        
    print repr(msg)
    
    time.sleep(2)
    tn.write('repairtcdinfo GetInfo 3\n')
    time.sleep(8)
    msg = tn.read_very_eager()
    print msg
    output = msg
    print repr(output)
    
    result = {}
    
    hoy = datetime.date.today ()
    Hora_Minutos = time.strftime("%H%M", time.localtime(time.time()))
    fechaactual =hoy.strftime("%b %d %Y")
    fechaActual =hoy.strftime("%Y")
    
    Mes_Dia = hoy.strftime ("%m%d")
    
    result ['formato1'] = Mes_Dia + Hora_Minutos + fechaActual
           
    tn.write('settime ' +result ['formato1'] + '\n')
    
    time.sleep(2)
    msg = tn.read_very_eager()
    print msg        
    print repr(msg)
    
    time.sleep(2)
    tn.write('repairtcdinfo GetInfo 3\n')
    time.sleep(8)
    msg = tn.read_very_eager()
    print msg
    output = msg
    print repr(output)
    
    time.sleep(2)
    tn.write('repairtcdinfo IncrementTSN 3\n')
    time.sleep(8)
    msg = tn.read_very_eager()
    print msg
    output = msg
    print repr(output)
    
    time.sleep(2)
    tn.write('repairtcdinfo GetInfo 3\n')
    time.sleep(8)
    msg = tn.read_very_eager()
    print msg
    output = msg
    print repr(output)
    
except socket.error:
    #time.sleep(3)
    tn = telnetlib.Telnet ('192.168.2.200',49152)
    time.sleep(3)
    print 'desconectando'