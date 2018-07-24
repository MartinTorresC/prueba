'''
Created on Mar 2, 2018

@author: User1
'''
import telnetlib
import socket
import os
import shutil
import ConfigParser
import sys
import time
import datetime
from PyQt4 import QtCore, QtGui, uic, QtNetwork
from PyQt4.QtNetwork import *
from PyQt4.QtCore import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from os.path import split


form_class = uic.loadUiType('IP900Gui.ui')[0]

class principal(QtGui.QMainWindow, form_class):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.iniciarPrueba = False
        self.btnStart.clicked.connect(self.iniciar)
        self.HostSN = ''   
           
        return
    def iniciar(self):
        self.lblShowMSG.setStyleSheet("background-color: cyan")
        self.lblShow.clear()
        self.lblShow_2.clear()
        self.lblShow_3.clear()
        self.lblShow_4.clear()           
        if self.btnStart.text() == 'I N I C I A R':
            self.btnStart.setText('C A N C E L A R')
            msg = 'INICIANDO PRUEBA...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            Serialcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR HOST SN:')
            
            if ok:
                if len(str(Serialcapturado)) != 12:
                    msg = 'FORMATO DE NUMERO DE HOST SN INCORRECTO...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                else:
                    self.HostSN = str(Serialcapturado)                
                    self.lblShow.setText('HOST SN:         ' + self.HostSN)
                    msg = 'NUMERO DE SERIE INTRODUCIDO: ' + str(Serialcapturado)
                    self.guardar_logs(msg)
            TSNcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR TSN:')
                    
            if ok:
                if len(str(TSNcapturado)) != 15:
                    msg = 'FORMATO DE NUMERO DE TSN INCORRECTO...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                            
                else:
                    self.TSN = str(TSNcapturado)                
                    self.lblShow_2.setText('TSN:                 ' + self.TSN)
                    msg = 'NUMERO DE SERIE TiVo INTRODUCIDO: ' + str(TSNcapturado)
                    self.guardar_logs(msg)
            MOCAcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR MOCA MAC:')
                            
            if ok:
                if len(str(MOCAcapturado)) != 12:
                    msg = 'FORMATO DE NUMERO DE MAC INCORRECTO...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                else:
                    self.MOCAMAC = str(MOCAcapturado)                
                    self.lblShow_3.setText('MOCA MAC:      ' + self.MOCAMAC)
                    msg = 'NUMERO DE MOCA MAC INTRODUCIDO: ' + str(MOCAcapturado)
                    self.guardar_logs(msg)
            EMACcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR EMAC:')
                                    
            if ok:
                if len(str(EMACcapturado)) != 12:
                    msg = 'FORMATO DE NUMERO DE MAC INCORRECTO...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                else:
                    self.EMAC = str(EMACcapturado)                
                    self.lblShow_4.setText('EMAC:              ' + self.EMAC)
                    msg = 'NUMERO DE EMAC INTRODUCIDO: ' + str(EMACcapturado)
                    self.guardar_logs(msg)
                    time.sleep(1)
                    #self.iniciarPrueba = True
                    self.conexion_telnet()
                    
            '''  
                                        self.btnStart.setText('I N I C I A R')
                                        msg = ' ****CICLO CANCELADO...****\n **** FORMATO INCORRECTO...****'
                                        self.lblShowMSG.setText(msg)
                                        self.guardar_logs(msg)
                                        self.iniciarPrueba = False
                                        self.lblShowMSG.setStyleSheet("background-color: orange") 
                                        return 
                                        
                                self.btnStart.setText('I N I C I A R')
                                msg = ' CICLO CANCELADO...\n **** FORMATO INCORRECTO...****'
                                self.lblShowMSG.setText(msg)
                                self.guardar_logs(msg)
                                self.iniciarPrueba = False
                                self.lblShowMSG.setStyleSheet("background-color: orange") 
                                return 
                                   
                        self.btnStart.setText('I N I C I A R')
                        msg = ' ****  CICLO CANCELADO...****\n**** FORMATO INCORRECTO...****'
                        self.lblShowMSG.setText(msg)
                        self.guardar_logs(msg)
                        self.iniciarPrueba = False
                        self.lblShowMSG.setStyleSheet("background-color: orange") 
                        return
                        
                    #self.conexion_telnet()          
                self.btnStart.setText('I N I C I A R')
                msg = ' **** CICLO CANCELADO...****\n **** FORMATO INCORRECTO...****'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                self.iniciarPrueba = False
                self.lblShowMSG.setStyleSheet("background-color: orange")
                return
            '''   
                                               
        self.btnStart.setText('I N I C I A R')
        #self.btnStart.setStyleSheet("background-color: green")
        msg = ' ***  PRUEBA CANCELADA...  ****\n'
        self.lblShowMSG.setText(msg)
        self.guardar_logs(msg)
        
        self.iniciarPrueba = False
        self.lblShowMSG.setStyleSheet("background-color: orange")
        return
        
    def conexion_telnet(self):
        try:
    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            output= tn.read_very_eager()
            time.sleep(2)
            #R = s.split('\n')
            print output
    
            print 'HDMI & AUDIO Video Test'
            time.sleep(0.5)
            tn.write('ipclient 192.168.2.3 80 eth0 http HDMI1.ts 0x00777777\n')
            
            time.sleep(0.5)
            output = tn.read_very_eager()
            print output
            time.sleep(0.5)
            msg = 'REALIZANDO PRUEBA DE VIDEO Y AUDIO HDMI'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            choice = QtGui.QMessageBox.question(self, 'HDMI AUDIO & VIDEO!',"Se Muestra Video HDMI y Audio?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if choice == QtGui.QMessageBox.Yes:
                msg = 'PRUEBA DE VIDEO Y AUDIO HDMI EXITOSA...'
                #self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                time.sleep(0.5)
                msg = 'REALIZANDO PRUEBA DE AUDIO OPTICO'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                
                choice = QtGui.QMessageBox.question(self, 'OPTICAL AUDIO!',"La Unidad Tiene Salida de Audio Optico?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                
                if choice == QtGui.QMessageBox.Yes:
                    
                    msg = 'PRUEBA DE AUDIO OPTICO EXITOSA...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                   
                    tn.write('ipclient disable \n')
                    time.sleep(2)
                    output = tn.read_very_eager()
                    print output
                    time.sleep(0.5)
                    print 'Bluetooth Test'
                    msg = 'REALIZANDO PRUEBA DE BLUETOOTH...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                    print 'Bluetooth Init'
                    tn.write ('bt init \n')
                    time.sleep(5)
                    output = tn.read_very_eager()
                    print output
                    time.sleep(2)
                    print 'Searching Device'
                    tn.write ('bt 7e:28:d4:14:f8:a1 \n')
                    time.sleep(35)
                    output = tn.read_very_eager()
                    print output
                    print 'Bluetooth Uninit'
                    tn.write ('bt uninit \n')
                    time.sleep(4)                    
                    output = tn.read_very_eager()
                    print output
                    time.sleep(1)
                    print 'MoCA Test 1150'
                    tn.write('mocaset 1150 0 \n')
                    time.sleep(1)
                    output = tn.read_very_eager()
                    print output
                    print "Getting MoCA Rate Value"
                    time.sleep(8)
                    tn.write('mocaget \n')
                    time.sleep(2)
                    output = tn.read_very_eager()
                    print output
                    print 'Stop MoCA 1150'
                    time.sleep(1)
                    tn.write('mocaset 1150 6 \n')
                    time.sleep(1)
                    output = tn.read_very_eager()
                    print output
                    time.sleep(1)
                    print 'MoCA Test 1600'
                    tn.write('mocaset 1600 0 \n')
                    time.sleep(1)
                    output = tn.read_very_eager()
                    print output
                    print "Getting MoCA Rate Value"
                    time.sleep(8)
                    tn.write('mocaget \n')
                    time.sleep(2)
                    output = tn.read_very_eager()
                    print output
                    print 'Stop MoCA 1150'
                    time.sleep(1)
                    tn.write('mocaset 1600 6 \n')
                    time.sleep(1)
                    output = tn.read_very_eager()
                    print output
                    self.iniciarPrueba = True
                    self.paso()
                else:
                    msg = 'PRUEBA DE AUDIO OPTICO FALLO...'
                    self.lblShowMSG.setText(msg)
                    self.guardar_logs(msg)
                    tn.write('ipclient disable')
            else:
                msg = 'PRUEBA DE VIDEO Y AUDIO HDMI FALLO...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                tn.write('ipclient disable')
                          
                    
            
        except socket.error:
    #time.sleep(3)
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(3)
            print 'desconectando' 
             
    def paso(self):
        if self.iniciarPrueba is True:
                            
            self.lblShowMSG.setStyleSheet("background-color: rgb(0,255,0)")
            msg = 'LA PRUEBA FUE EXITOSA.... \nPRUEBA FINALIZADA'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.iniciar()
            self.iniciarPrueba = False
            self.btnStart.setText('I N I C I A R')
            self.iniciar()
            
                
        else:
            msg = 'LA PRUEBA NO SE HA INICIADO...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.setStyleSheet("background-color: orange")

        #return  
           
    def guardar_logs(self, msg):
        #filename = "/Users/User1/Desktop/LogsSerial/" + self.HostSN +".txt"
        #with open(filename,"w") as f:
        horaactual = time.strftime("%H:%M:%S", time.localtime(time.time())) + " "
        fechaactual = str(datetime.datetime.now().date()) + " "
        h_f = fechaactual+horaactual
        self.txtLog.appendPlainText(h_f + msg)
        #    print f
        #    f.write('\t' + h_f + msg +'\n')
        #f.close()
          
        #return    
app = QtGui.QApplication(sys.argv)
miVentana = principal(None)
miVentana.show()
app.exec_()