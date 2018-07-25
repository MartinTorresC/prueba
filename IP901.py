'''
Created on Mar 14, 2018

@author: User 1
'''
import telnetlib
import socket
#import os
#import shutil
#import ConfigParser
import sys
import time
import datetime
import logging
from PyQt4 import QtCore, QtGui, uic, QtNetwork
from PyQt4.QtNetwork import *
from PyQt4.QtCore import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from os.path import split
import db_ip90x_test
from db_class import UnitDetail, MXDBAccess, msg_para_json, guardar_logs, f_h
import ConfigParser

from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy import schema, types, create_engine

from ConfigParser import SafeConfigParser

#form_class = uic.loadUiType('IP900Gui.ui')[0]
form_class = uic.loadUiType('IP90xRepairGui.ui')[0]

class principal(QtGui.QMainWindow, form_class):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.iniciarPrueba = False
        self.btnStart.clicked.connect(self.iniciar)
        self.HostSN = ''   
        self.TSNcapturado = ''
        self.MACcapturado = ''
        self.SKUcapturado = ''
        self.Error ='' 
        self.Informacion_DB = {}
        Error = ''
        #tn = ''
        
        #retVal = self.read_config('STATION_INFO')
        self.datos = UnitDetail()
        retVal = self.read_config('STATION_INFO')
        self.Informacion_DB = self.datos.guardarDatos
        
        self.Informacion_DB['Test_Station'] = retVal['test_station']
        #self.Informacion_DB['Model'] = 'IP901'
        print retVal
        self.Informacion_DB['Station'] = retVal['station'] 
        print self.Informacion_DB
        
        encabezados = [' DESCRIPCION DE LA PRUEBA ', ' RESULTADO ']
        self.tblResultado.setColumnCount(len(encabezados))
        self.tblResultado.setHorizontalHeaderLabels(encabezados)
        self.tblResultado.resizeColumnsToContents()
        self.tblResultado.setRowCount(5)
        self.tblResultado.setColumnCount(2)
        
        retVal = self.read_config('STATION_INFO')
        #self.datos = UnitDetail()
        self.Informacion_DB_RTDS = self.datos.guardarDatosRTDS
        #print self.Informacion_DB_RTDS
        self.actionRe_Imprimir_Etiqueta.triggered.connect(self.Reimprimir_Etiqueta)
        #self.actionEjecutar_Prueba_Funcional.triggered.connect(self.conexion_telnet)
        '''
        self.actionEjecutar_Prueba_Funcional.triggered.connect(self.conexion_telnet)
        self.actionEjecutar_Prueba_de_Bluetooth.triggered.connect(self.Verificacion_Bluetooth)
        self.actionEjecutar_Prueba_de_Video.triggered.connect(self.Verificacion_Audio_Video)
        self.actionEjecutar_Prueba_de_MoCA_1150MHz.triggered.connect(self.Verificacion_MOCA1150)
        self.actionEjecutar_Prueba_de_MoCA_1600_MHz.triggered.connect(self.Verificacion_MOCA1600)
        '''  
        return
    def read_config(self, section):
        filename = "config_ip90.conf"
        Config = ConfigParser.ConfigParser()
        Config.read(filename)
        dict1 = {}
        try:
            options = Config.options(section)
        except Exception, e:
            msg = "ERROR AL LEER ARCHIVO DE CONFIGURACION: " + str(e)
            result_msg = msg_para_json("F", "ERR1201", msg, str(e))
            return (result_msg)
        for option in options:    
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        
        if bool(dict1):
            dict1['result'] = "P"
        else:
            dict1 = msg_para_json("F", "ERR1202", "SECCION DEL ARCHIVO DE CONFIGURACION ESTA VACIA")
            
        return dict1    
    def Inicializar (self):
        
        
        self.lblShowMSG.setStyleSheet("background-color: cyan")
        self.lblscan.setStyleSheet('background-color:None')
        self.lblShow.clear()
        self.lblShowMSG.clear()
        self.lblShow_2.clear()
        self.lblShow_3.clear()
        self.lblShow_4.clear()
        self.lblscan.clear()
        
        self.tblResultado.setItem(0,0, QTableWidgetItem("HDMI TEST"))
       
        
        self.tblResultado.item(0,0).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(0,1, QtGui.QTableWidgetItem("")) 
        self.tblResultado.item(0,1).setBackground(QtGui.QColor(255,255,255))
        
        self.tblResultado.setItem(1,0, QtGui.QTableWidgetItem("OPTICAL AUDIO TEST")) 
        self.tblResultado.item(1,0).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(1,1, QTableWidgetItem(""))
        self.tblResultado.item(1,1).setBackground(QtGui.QColor(255,255,255)) 
        self.tblResultado.setItem(2,0, QtGui.QTableWidgetItem("BLUETOOTH TEST")) 
        self.tblResultado.item(2,0).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(2,1, QTableWidgetItem(""))
        self.tblResultado.item(2,1).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(3,0, QtGui.QTableWidgetItem("MOCA 1150 MHz TEST")) 
        self.tblResultado.item(3,0).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(3,1, QTableWidgetItem(""))
        self.tblResultado.item(3,1).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(4,0, QtGui.QTableWidgetItem("MOCA 1600 MHz TEST"))
        self.tblResultado.item(4,0).setBackground(QtGui.QColor(255,255,255))
        self.tblResultado.setItem(4,1, QTableWidgetItem(""))
        self.tblResultado.item(4,1).setBackground(QtGui.QColor(255,255,255))            
        #self.Informacion_DB.clear()
        #print self.Informacion_DB
        return
    def clear_data(self):

        print "EJECUTANDO RUTINA PARA LIMPIAR DATOS DE LA UNIDAD ANTERIOR"
        
        for key in self.datos.guardarDatos.iterkeys():
            print "LIMPIANDO DATOS DE LA UNIDAD ANTERIOR"
            print key
            if key == 'Station':
                print'Estoy en la estacion'
                pass
            elif key == 'Test_Station':
                print'Estoy en la Test estacion'
                pass
            
            elif key == 'Model':
                pass  
            else:
                self.datos.guardarDatos[key]='X'
        print self.datos.guardarDatos
        return
    
    def iniciar(self):
        self.clear_data()
        print self.Informacion_DB
        retVal = self.read_config('STATION_INFO')
        self.Informacion_DB['Test_Station'] = retVal['test_station']
        #self.Inicializar()
        self.Station.setText('ESTACION  DE '  + retVal['test_station'])
     
        self.comboBox.currentIndex()
        self.comboBox.currentText()
        print self.comboBox.currentText()
        self.Informacion_DB['Model'] = self.comboBox.currentText()
        
        if self.comboBox.currentText() == 'IP900':
            print 'PROCESANDO MODELO ' + self.comboBox.currentText()         
            self.MODELO_IP900()
            
        elif self.comboBox.currentText() == 'IP901':
            print 'PROCESANDO MODELO '  + self.comboBox.currentText()
            self.MODELO_IP901()
        
        else:
            msg = '!!!! SELECCIONE MODELO !!!!'
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.setText(msg)
            #self.guardar_logs(msg)
            self.btnStart.setText('I N I C I A R')                  
            self.iniciarPrueba = False
            self.lblShowMSG.setStyleSheet("background-color: orange")
            return
        
    def MODELO_IP901(self):
        
        self.Inicializar()
        self.clear_data()
        
        if self.btnStart.text() == 'I N I C I A R':
            self.btnStart.setText('C A N C E L A R')
            msg = 'INICIANDO PRUEBA...'
            self.lblShowMSG.setText(msg)
            self.Informacion_DB = self.datos.guardarDatos
            print self.Informacion_DB
            print self.Informacion_DB_RTDS
            self.TSNcapturado, ok = QInputDialog.getText(self, 'IP90X TEST... ', 'ESCANEAR TSN:') ###### TSN ETIQUETA DE LA UUT #####
            self.guardar_logs(msg)         
            msg ='PROCESANDO MODELO ' + self.comboBox.currentText()
            self.guardar_logs(msg)
            #self.lblShowMSG.setText(msg)
                        
            print ok
            if not ok:
                self.PruebaCancelada ()
                return
            else:    
                retResult = self.Verificar_formatoTSN (self.TSNcapturado)
                print retResult
                self.TSN_Scan = str(self.TSNcapturado)                
                self.lblShow_2.setText('TSN:                 ' + self.TSN_Scan)
                self.Informacion_DB['TSN_Scanned']= self.TSN_Scan
                #self.Informacion_DB_RTDS['TSN']= self.TSN_Scan
                #retVal = self._process_guardar_datosRTDS(self.Informacion_DB_RTDS)
                
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]           
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
            retVal = self.read_config('STATION_INFO')
                               
            if retVal['test_station'] == 'PRINT_LABEL': ######  ESTACION DE IMPRESION DE ETIQUETAS  #######
                
                retResult = self.consulta_TSN(self.TSN_Scan) ###### CONSULTA SI EL TSN SE PROCESO EN LA ESTACION DE FUNCIONAL Y SI PASO LA PRUEBA ######
                
                msg = 'INICIANDO PRUEBA DE IMPRESION DE ETIQUETAS...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                
                if retResult['result'] == "F":
                    
                    msg = 'NUMERO DE TSN NO SE HA PROCESADO EN FUNCIONAL...'
                    result = "F"
                    Errorcode = 'ERROR 0120'
                    ErrorDescription = 'No se encontro el numero de TSN'
                    self.Informacion_DB['Failure_Code']= Errorcode
                    self.Informacion_DB['Failure_Description']= ErrorDescription
                    self.Informacion_DB['Result'] = result
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    self.Falla(msg)
                    return
                #print retResult 
                if retResult['Resultado'] == "F":
                    msg = 'LA UNIDAD NO PASO LA PRUEBA FUNCIONAL...'
                    result = "F"
                    Errorcode = 'ERROR 0120'
                    ErrorDescription = 'Ha ocurrido un Error con la rutina de consulta en DB'
                    self.Informacion_DB['Failure_Code']= Errorcode
                    self.Informacion_DB['Failure_Description']= ErrorDescription
                    self.Informacion_DB['Result'] = result
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    self.Falla(msg)
                    return
                
                self.TSN_Scan = retResult['TSN_NEW']           ##### Contiene el Numero de TSN Interno de la Unidad
                self.Temp_TSN_Scan = retResult['TSN_Scanned']  ##### Contiene el Numero de TSN Escaneado de la Etiqueta
                self.TSN_New_Obtained = retResult['TSN_NEW']   ##### Contiene el Numero de TSN Interno de la Unidad
                self.MAC1_Scan = retResult['MAC1_GET']         ##### Contiene el Numero de MAC Interno de la Unidad
                self.MAC2_Scan = retResult['MAC2_GET']         ##### Contiene el Numero de MAC Interno de la Unidad
                
                print retResult
                
                retResult = self.actualizarRegistro (self.Temp_TSN_Scan,self.TSN_New_Obtained)  ##### Actualiza la celda correspondiente al Nuevo TSN en la Tabla de la base de Datos RTDS.##### 
                print retResult
                
                if retResult['result'] == "F":
                    msg = retResult ["errorDescription"]
                    self.Informacion_DB['Failure_Code']= retResult ["errorCode"]
                    self.Informacion_DB['Failure_Description']= retResult ["errorDescription"]
                    self.Informacion_DB['Result'] = retResult ["result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    self.Falla(msg)
                    print retVal
                    return
                msg = 'SE ACTUALIZO TSN EN LA BASE DE DATOS...'
                self.guardar_logs(msg)
                                  
                retResult = self.consulta_TSN_RTDS(self.Temp_TSN_Scan) ###### CONSULTA BASE DE DATOS  TABLA RTDS PARA OBTENER DATOS #####
                print retResult
                if retResult['result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                self.Informacion_DB['SKU_New']= retResult['SKU']              
                self.Temp_SKU_New = retResult['SKU']    #####Contiene el Nuevo SKU B o P Segun Corresponda ####
                print self.Temp_SKU_New
                
                if retResult['result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
                
                retResult = self.conexionSTC_telnet()    ###### RUTINA DE COMPARACION DE  DATOS INTERNOS VS OBTENIDOS DE LA BASE DE DATOS ######
                print retResult
                
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
                
                print self.Informacion_DB
                print "SI PASO LA PRUEBA FUNCIONAL" 
                
                retResult = self.Print_Delete(self.TSN_New_Obtained,self.MAC1_Scan,self.MAC2_Scan,self.Temp_SKU_New)
                print retResult
                
                if retResult['Result'] == "F":
                    print "Falla de Impresion de Etiquetas"
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    return
                
                print retResult
                
                self.iniciarPrueba = True
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                retVal = self._process_guardar_datos(self.Informacion_DB)
                self.paso()                                        #################Termina Exitosamente la Prueba de Impresion de Etiquetas ##############
                return 
               
            retResult = self.consulta_TSN_RTDS(self.TSN_Scan)
            print retResult
              
            if retResult['result'] == "F":
                    
                    msg = 'NUMERO DE TSN NO SE HA RECIBIDO...'
                    result = "F"
                    Errorcode = 'ERROR_0120'
                    ErrorDescription = 'No se encontro el numero de TSN'
                    self.Informacion_DB['Failure_Code']= Errorcode
                    self.Informacion_DB['Failure_Description']= ErrorDescription
                    self.Informacion_DB['Result'] = result
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    self.Falla(msg)
                    return
            self.Informacion_DB['SKU_New']= retResult['SKU']      
            self.MACcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR MAC1:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoMAC (self.MACcapturado)
                print retResult
                self.MAC1_Scan = str(self.MACcapturado)                
                self.lblShow_3.setText('MAC1:               ' + self.MAC1_Scan)
                               
                self.Informacion_DB['MAC1_Scanned']= self.MAC1_Scan
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
            self.MACcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR MAC2:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoMAC (self.MACcapturado)
                print retResult
                self.MAC2_Scan = str(self.MACcapturado)                
                self.lblShow_4.setText('MAC2:               ' + self.MAC2_Scan)
                               
                self.Informacion_DB['MAC2_Scanned']= self.MAC2_Scan
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                        
            self.SKUcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR SKU:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoSKU (self.SKUcapturado)
                print retResult
                self.SKU_Scan = str(self.SKUcapturado) 
                self.Informacion_DB['SKU_Scanned']= self.SKU_Scan               
                self.lblShow.setText('SKU:                 ' + self.SKU_Scan)
                self.iniciarPrueba = True
                self.lblShowMSG.repaint()  
                           
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return                                           
            
            print self.Informacion_DB
            retResult = self.conexionSTC_telnet()
            print retResult
                      
            if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                retVal = self._process_guardar_datos(self.Informacion_DB)
                print retVal
                return 
            
            print retResult
            
            retResult = self.conexion_telnet()
            
            
            if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                retVal = self._process_guardar_datos(self.Informacion_DB)
                print retVal
                return
            
            retVal = self.read_config('STATION_INFO')
            print retVal['test_station']
                               
            if retVal['test_station'] == 'FUT': ######  ESTACION DE FUT REQUIERE INCREMENTO DE TSN  #######           
                retResult = self.Incremento_TSN()
                print retResult
                print "LA ESTACION FUE CONFIGURADA COMO FUT"
                
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
            print self.Informacion_DB
            print retResult
            print self.Informacion_DB
            
            self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
            self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
            self.Informacion_DB['Result'] = retResult ["Result"]
            retVal = self._process_guardar_datos(self.Informacion_DB)
            self.paso()
            print retVal
             
        return
            
    def MODELO_IP900(self):
        
        self.Inicializar()
        if self.btnStart.text() == 'I N I C I A R':
            self.btnStart.setText('C A N C E L A R')
            msg = 'INICIANDO PRUEBA...'
            self.lblShowMSG.setText(msg)

            self.Informacion_DB = self.datos.guardarDatos
            self.TSNcapturado, ok = QInputDialog.getText(self, 'IP90X TEST... ', 'ESCANEAR TSN:') ###### TSN ETIQUETA DE LA UUT #####
            self.guardar_logs(msg)         
            msg ='PROCESANDO MODELO ' + self.comboBox.currentText()
            self.guardar_logs(msg) 
            
            print ok
            if not ok:
                self.PruebaCancelada ()
                return
            else:    
                retResult = self.Verificar_formatoTSN (self.TSNcapturado)
                print retResult
                self.TSN_Scan = str(self.TSNcapturado)                
                self.lblShow_2.setText('TSN:                 ' + self.TSN_Scan)
                self.Informacion_DB['TSN_Scanned']= self.TSN_Scan
                               
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]           
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
            retVal = self.read_config('STATION_INFO')
                               
            if retVal['test_station'] == 'PRINT_LABEL': ######  ESTACION DE IMPRESION DE ETIQUETAS  #######
                
                msg = 'INICIANDO PRUEBA DE IMPRESION DE ETIQUETAS...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)               
                msg = 'AUN NO ESTA DISPONIBLE LA IMPRESION DE ETIQUETAS PARA IP900...'
                self.Falla(msg)
                return 
                             
            self.MACcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR MOCA MAC:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoMAC (self.MACcapturado)
                print retResult
                self.MAC1_Scan = str(self.MACcapturado)                
                self.lblShow_3.setText('MAC1:               ' + self.MAC1_Scan)
                               
                self.Informacion_DB['MAC1_Scanned']= self.MAC1_Scan
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                
            self.MACcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR EMAC:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoMAC (self.MACcapturado)
                print retResult
                self.MAC2_Scan = str(self.MACcapturado)                
                self.lblShow_4.setText('MAC2:               ' + self.MAC2_Scan)
                               
                self.Informacion_DB['MAC2_Scanned']= self.MAC2_Scan
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return
                        
            self.HostSNcapturado, ok = QInputDialog.getText(self, 'IP900 TEST... ', 'ESCANEAR HOST SN:') 
                           
            if not ok:
                self.PruebaCancelada()
                return
            else:
                  
                retResult = self.Verificar_formatoHOST (self.HostSNcapturado)
                print retResult
                self.HostSN_Scan = str(self.HostSNcapturado) 
                #self.Informacion_DB['HostSN_Scanned']= self.HostSN_Scan               
                self.lblShow.setText('Host SN:            ' + self.HostSN_Scan)
                self.iniciarPrueba = True
                self.lblShowMSG.repaint()
                  
                self.Informacion_DB['HostSN_Scanned']= self.HostSN_Scan
                           
                if retResult['Result'] == "F":
                    self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                    self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                    self.Informacion_DB['Result'] = retResult ["Result"]
                    retVal = self._process_guardar_datos(self.Informacion_DB)
                    print retVal
                    return                                           
            
            print self.Informacion_DB
            
            retResult = self.conexionSTC_telnet()
            print retResult
                      
            if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                retVal = self._process_guardar_datos(self.Informacion_DB)
                print retVal
                return 
            
            print retResult
            retResult = self.conexion_telnet()
            
            if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                retVal = self._process_guardar_datos(self.Informacion_DB)
                print retVal
                return
                       
           
            print retResult
            print self.Informacion_DB
            
            self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
            self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
            self.Informacion_DB['Result'] = retResult ["Result"]
            retVal = self._process_guardar_datos(self.Informacion_DB)
            self.paso()
            print retVal
             
        return 

    def consulta_TSN(self, TSN_Scan):
        
        retResult =self. read_config('STATION_INFO')
        if retResult['result'] == "F":
            return(retResult)
        
        tsa = retResult['test_station']
        tsp = retResult['prev_station']
        
        print retResult
         
        db = MXDBAccess()
        retResult = db.db_connection()
        print "Status de conexion a la base de datos"
        #print retResult
        
        # VERIFICAR SI HAY UN ERROR AL CONECTARSE A LA BASE DE DATOS
        if retResult['result'] == "F":
            #print retResult['errorCode']
            #print retResult['errorDescription']
            #print retResult['failureReason']
            return (retResult)
        
        buscar_sn = db.consultar_sn_(TSN_Scan,tsa,tsp)
        print buscar_sn
        #print buscar_sn['passOK']
        
        #print len(buscar_sn['Datos'])
        if buscar_sn['result'] == "F":
            errorDesc =  'No se encontro el numero de TSN'
            result_msg = msg_para_json("F", "ERR0950", errorDesc, "NUMERO DE TSN NO REGISTRADO")
        else:
            #print 'Numero de serie encontrado'
            #print buscar_sn['Datos'][0]['Hora'], buscar_sn['Datos'][0]['Fecha'] 
            #print buscar_sn['Datos'][0]['TCD_Info_Current']
            result_msg = msg_para_json("P")
            result_msg['tcdInfo'] = buscar_sn['Datos']['TCD_Info_New']
            result_msg['TSN_NEW'] = buscar_sn['Datos']['TSN_New']
            result_msg['MAC1_GET'] = buscar_sn['Datos']['MAC1_Interno']
            result_msg['MAC2_GET'] = buscar_sn['Datos']['MAC2_Interno']
            result_msg['Resultado'] = buscar_sn['Datos']['Result']
            result_msg['TSN_Scanned'] = buscar_sn['Datos']['TSN_Scanned']
            
            
            print buscar_sn['Datos']['Hora'], buscar_sn['Datos']['Fecha'] 
            print buscar_sn['Datos']['TCD_Info_Current']
            print buscar_sn['Datos']['Result']
            print buscar_sn['Datos']['Test_Station']
            print buscar_sn['Datos']['TCD_Info_Current']
            
        return (result_msg)
    
    def consulta_TSN_RTDS(self, TSN_Scan):
        db = MXDBAccess()
        tabla = 'ip90x_rcvd_tbl' 
        retResult = db.db_connection(tabla)
        
        print "Status de conexion a la base de datos"
        #print retResult
        
        # VERIFICAR SI HAY UN ERROR AL CONECTARSE A LA BASE DE DATOS
        if retResult['result'] == "F":
            #print retResult['errorCode']
            #print retResult['errorDescription']
            #print retResult['failureReason']
            return (retResult)
        
        print TSN_Scan
        buscar_sn = db.consultar_SN_(TSN_Scan)
        
        #print buscar_sn['passOK']
        
        #print len(buscar_sn['Datos'])
        if buscar_sn['result'] == "F":
            errorDesc =  'No se encontro el numero de TSN'
            result_msg = msg_para_json("F", "ERR0950", errorDesc, "NUMERO DE TSN NO REGISTRADO")
        else:
            #print 'Numero de serie encontrado'
            #print buscar_sn['Datos'][0]['Hora'], buscar_sn['Datos'][0]['Fecha'] 
            #print buscar_sn['Datos'][0]['TCD_Info_Current']
            result_msg = msg_para_json("P")
            
            result_msg['TSN'] = buscar_sn['Datos'][0]['TSN']
            result_msg['Receiving_Date'] = buscar_sn['Datos'][0]['Receiving_Date']
            result_msg['SKU'] = buscar_sn['Datos'][0]['SKU']
            result_msg['Packing_Date'] = buscar_sn['Datos'][0]['Packing_Date']
            result_msg['Status'] = buscar_sn['Datos'][0]['Status']
            result_msg['XML_Info'] = buscar_sn['Datos'][0]['XML_Info']
            result_msg['TSN_New'] = buscar_sn['Datos'][0]['TSN_New']
        
           
        return (result_msg)
    
    def _process_guardar_datos(self, Informacion_DB):
        db = MXDBAccess()
        retResult = db.db_connection()
        print "Status de conexion a la base de datos"
        print retResult
        #print GuardarDatos
        retVal = db.insert_data(Informacion_DB)
        
        return
    def _process_guardar_datosRTDS(self, Informacion_DB_RTDS):

        db = MXDBAccess()
        tabla = 'ip90x_rcvd_tbl' 
        retResult = db.db_connection(tabla)
        print "Status de conexion a la base de datos"
        print retResult
        #print GuardarDatos
        retVal = db.insert_data(Informacion_DB_RTDS)
        
        return
    def actualizarRegistro(self,Temp_TSN_Scan,TSN_New_Obtained):
    
    
        try:
            db_host = "192.168.200.38"
            db_db = "ip90x_db"
            db_table = "ip90x_rcvd_tbl" 
            
            #print db_host, db_db, db_table
            #self.db = create_engine('mysql+mysqldb://edemsamodems:contec@' + db_host + '/' + db_db)
            db = create_engine('mysql+mysqldb://ip90user:password321@' + db_host + '/' + db_db)
            db.echo = True  # Try changing this to True and see what happens
            metadata = schema.MetaData(db)
            #print "si se conecto"
            #Linea Original
            #datos = Table('arris_tbl', metadata, autoload=True)
            datos = Table(db_table, metadata, autoload=True)
            #print "despues de la conexion a la tabla"
            
            cursor_data = datos
            #table.update().where(table.c.id==7).values(name='foo')
            #print self.Informacion_DB_RTDS
            valores = {}
            valores['TSN_New'] = TSN_New_Obtained
            print  valores['TSN_New']
            print self.Temp_TSN_Scan
            #valores['TCD_Info_New'] = "NOMAS UN OTRO DATO DE PRUEBA"
            s = cursor_data.update().where(cursor_data.c.TSN == Temp_TSN_Scan).values(valores)
            rs = s.execute()
            
            #print rs
            jmsg = msg_para_json("P")
        
        except Exception, e:
            print e
            print "Ha ocurrido el error", e
            frc = sys.exc_info()
            err_code = 'ERR0030'
            msg = 'Error al abrir o conectarse a la DB'
            jmsg = msg_para_json("F", err_code, msg, frc)
            #return (jmsg)
        
        # Este comando es para cerrar la conexion a la base de datos
        db.dispose()
        return (jmsg)
    
    def Print_Delete (self,TSN_New_Obtained,MAC1_Scan,MAC2_Scan,Temp_SKU_New):
        
        result = 'F'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        try:
            
    ### ***************************************************************************************** ###
            modelo                  = "IP901"
            modoImpresion           = "IP"
            datosImprimir           = {}
            datosImprimir['TSN']    = self.TSN_New_Obtained
            datosImprimir['MAC1']   = self.MAC1_Scan
            datosImprimir['MAC2']   = self.MAC2_Scan
            datosImprimir['SKU']    = self.Temp_SKU_New
            
            print "Corriendo la rutina crear_archivo..."
            retVal = self.crear_archivo(modelo, datosImprimir)
            print retVal
            print "Corriendo la rutina imprimirEtiqueta..."
            retVal = self.imprimirEtiqueta(modelo, modoImpresion)
            print retVal
    
    
    ### ***************************************************************************************** ###
            print self.Informacion_DB_RTDS            
            PRINTOK = QtGui.QMessageBox.question(self, 'PRINT LABEL & DELETE!',"Se Imprimio Correctamente la etiqueta?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if PRINTOK == QtGui.QMessageBox.No:
                
                msg = 'LA ETIQUETA NO SE IMPRIMIO CORRECTAMENTE...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)           
                self.lblShowMSG.repaint()
                result ='F'
                Errorcode = 'ERROR_0121'
                ErrorDescription = 'Error al Imprimir Etiqueta'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['Print_Status']= result
                self.Falla(msg)
                return (retvalue)
            msg = 'LA ETIQUETA SE IMPRIMIO CORRECTAMENTE...'
            self.guardar_logs(msg)                   
            time.sleep(2)
            tn = telnetlib.Telnet ('192.168.2.200',49152)
            time.sleep(2)
            msg = 'PRUEBA DE BORRADO DE OBJETOS'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            output= tn.read_very_eager()
            self.lblShowMSG.repaint()
            print output  
            tn.write('deleteobject\n')
            time.sleep(5)
            msg = tn.read_very_eager()
            print msg
            print "Prueba de Borrado de Objetos"
            self.guardar_logs (msg)
            self.output = msg
            tn.write('reboot\n')
            time.sleep(5)
            msg = tn.read_very_eager()
            print msg
            print "Reboot"
            result = 'P'
            self.guardar_logs (msg)
            
        except:
            result = "F"
            Errorcode = 'ERROR_0121'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Impresion y Borrado de Objetos'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        return (retvalue)
    def Reimprimir_Etiqueta (self):
         
        result = 'F'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        try:
            
    ### ***************************************************************************************** ###
            modelo                  = "IP901"
            modoImpresion           = "IP"
                       
            print "Corriendo la rutina imprimirEtiqueta..."
            retVal = self.imprimirEtiqueta(modelo, modoImpresion)
            print retVal
    
    
    ### ***************************************************************************************** ###            
        except:
            result = "F"
            Errorcode = 'ERROR_0121'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Re-Impresion de Etiquetas'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        
        return 
         
    def abrirImpresora(self,modelo, opciones=None):
        result_msg = {}
        try:
            retResult =self. read_config('PRINT_INFO')
            if retResult['result'] == "F":
                return(retResult)
            
            if modelo.startswith("IP901"):
                print "EXTRAYENDO IP DE IMPRESORA 1 PARA EL MODELO : %s " % (modelo)
                ip = retResult['printer_1_ip']
            else:
                print "EXTRAYENDO IP DE IMPRESORA 1 PARA EL MODELO : %s " % (modelo)
                ip = retResult['printer_1_ip']
                
            puertoTCP = int(retResult['print_port'])
            
        except Exception, e:
            result_msg = msg_para_json('F', 'ERR0066', "ERROR AL OBTENER INFO DE IP DE ARCHIVO DE CONFIGURACION: " + str(e))
            return (result_msg)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # server_address = (ip, 6101)
            server_address = (ip, puertoTCP)
            print >> sys.stderr, 'CONECTANDO A IMPRESORA: %s EN PUERTO %s' % server_address
            sock.connect(server_address)
            result_msg = msg_para_json("P")
            result_msg['socket'] = sock
            return (result_msg)
        except Exception, e:
            result_msg = msg_para_json('F', 'ERR0064', "ERROR EN LA RUTINA IMPRIMIRIP AL TRATAR DE CONECTARSE A LA IMPRESORA: " +  str(e))
            return (result_msg)
    def crear_archivo(self,modelo, infoImprimir, opciones=None):
            jmsg = {}
            
            try:
                if modelo.startswith("IP901"):
                    print "CREANDO ARCHIVO DE ETIQUETA PARA MODELO: " + modelo
                    f = open('ip90x_label.txt', 'w')
                    terminacionCampo = "^FS"
                    inicioCampo = "^FD"
                    terminacionLinea = "\n"
                    comandoInicial = '^XA' + terminacionLinea
                    labelHome = "07,20"
                    configurarHome = '^LH' + labelHome + terminacionCampo + terminacionLinea
                    fontSize = "25,25"
                    fontName = "E:AVENIRLL.FNT"
                    f.write(comandoInicial)
                    f.write(configurarHome)
                    
                    f.write("^FO130,60^A@N,28,25,E:AVENIRLL.FNT^FDMODEL: TCDA95000^FS" + terminacionLinea)
                    
                    f.write("^FO0,90^A@N," + fontSize + "," + fontName + inicioCampo + "TSN: " + infoImprimir["TSN"] + terminacionCampo + terminacionLinea)
                    f.write("^FO0,115^GB450,0,30"+ terminacionCampo + terminacionLinea)
                    f.write("^FR^FO25,115^BY2,1.48^BCN,30,N,N,N" + inicioCampo + infoImprimir["TSN"] + terminacionCampo + terminacionLinea)
                    
                    f.write("^FO0,155^A@N," + fontSize + "," + fontName + inicioCampo + "MAC1: " + infoImprimir["MAC1"] + terminacionCampo + terminacionLinea)
                    f.write("^FO0,179^GB381,0,30" + terminacionCampo + terminacionLinea)
                    f.write("^FR^FO25,179^BY2,1.48^BCN,30,N,N,N" + inicioCampo + infoImprimir["MAC1"] + terminacionCampo + terminacionLinea)
                    
                    f.write("^FO0,220^A@N," + fontSize + "," + fontName + inicioCampo + "MAC2: " + infoImprimir["MAC2"] + terminacionCampo + terminacionLinea)
                    f.write("^FO0,244^GB381,0,30" + terminacionCampo + terminacionLinea)
                    f.write("^FR^FO25,244^BY2,1.48^BCN,30,N,N,N" + inicioCampo + infoImprimir["MAC2"] + terminacionCampo + terminacionLinea)
                    
                    f.write("^FO0,285^A@N," + fontSize + "," + fontName + inicioCampo + "SKU:" + infoImprimir["SKU"] + terminacionCampo + terminacionLinea)
                    f.write("^FO0,309^GB271,0,30"  + terminacionCampo + terminacionLinea)
                    f.write("^FR^FO25,309^BY2,1.48^BCN,30,N,N,N" + inicioCampo + infoImprimir["SKU"] + terminacionCampo + terminacionLinea)
                    
                    f.write("^FO403,315^A@N,25,25,E:AVENIRLL.FNT^FD" + self.fecha_hora_actual()['formato6'] + terminacionCampo + terminacionLinea)
                    
                    f.write('^PQ1,0,0,N\n')
                    f.write('^XZ\n')
                    
                    #f.write('ARCHIVO CREADO EXITOSAMENTE, SOLO FALTA EL CODIGO PARA LA ETIQUETA!!!!!')
                    f.close()
                    jmsg = msg_para_json('P')
                    #return (jmsg)
                    
                    
            except Exception, e:
                jmsg = msg_para_json('F', 'ERR0055', "ERROR EN LA RUTINA CREAR ARCHIVO " + str(e))
                #return (jmsg)
            
            return (jmsg)
     
    def imprimirIP(self,modelo, opciones=None):
        jmsg = {}
        '''
        try:
            retResult = read_config('PRINT_INFO')
            ip = retResult['printer_1_ip']
            puertoTCP = int(retResult['print_port'])
        except Exception, e:
            jmsg = msg_para_json('F', 'ERR0066', "ERROR AL OBTENER INFO DE IP DE ARCHIVO DE CONFIGURACION: " + str(e))
            return (jmsg)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # server_address = (ip, 6101)
            server_address = (ip, puertoTCP)
            print >> sys.stderr, 'CONECTANDO A IMPRESORA: %s EN PUERTO %s' % server_address
            sock.connect(server_address)
        except Exception, e:
            jmsg = msg_para_json('F', 'ERR0064', "ERROR EN LA RUTINA IMPRIMIRIP AL TRATAR DE CONECTARSE A LA IMPRESORA: " +  str(e))
            return (jmsg)
        '''
        try:
            if modelo.startswith('IP901'):
                # PARA LOS DEMAS MODELO SOLO IMPRIMIR LA ETIQUETA DE IDS
                retVal = self.abrirImpresora(modelo)
                if retVal['result'] == "F":
                    return(retVal)
                sock = retVal['socket']
                f = open('ip90x_label.txt', 'r')
                zplCMDIDS = f.read()
                f.close()
                msg = '\n'+ zplCMDIDS
                self.guardar_logs(msg)
                print >> sys.stderr, 'Enviando: \n "%s"' % zplCMDIDS
                sock.sendall(zplCMDIDS)
                sock.close()
            
            jmsg = msg_para_json('P')
            return (jmsg)
        
        except Exception, e:
            print e
            jmsg = msg_para_json('F', 'ERR0062', str(e))
            return (jmsg)
    def imprimirEtiqueta(self,modelo, modo, opciones=None):
        if modo == 'SERIAL':
            retVal = self.imprimirSerial(modelo, opciones)
            return (retVal)
            
        elif modo == "IP":
            retVal = self.imprimirIP(modelo, opciones)
            return (retVal)

    def imprimirSerial(self,modelo, opciones=None):
        try:
            retResult = read_config('SERIAL_PORT')
            if retResult['result'] == "F":
                return(retResult)
    
            puertoCOM = retResult['puerto'] 
            print "LA ETIQUETA SE ENVIARA AL PUERTO : %s" % (puertoCOM) 
        except Exception, e:
            jmsg = msg_para_json('F', 'ERR0063', str(e))
            return (jmsg)
    
        try:
            print 'Creando el comando para configuracion de la etiqueta...'
            comando = Popen("CMD /C net use " + puertoCOM + " \\\\\\PC-WM-NVM-PKI-001\\110Xi4-USB", stdout=PIPE, stderr=PIPE)
            out, error = comando.communicate()
            print 'Comando creado...'
            msg = 'IMPRIMIENDO ETIQUETA...'
            print msg
            
            if modelo.startswith('TG1682'):
                print 'MODELO: TG1682'
                comando = Popen("CMD /C copy test_label.txt " + puertoCOM, stdout=PIPE, stderr=PIPE)
                out, error = comando.communicate()
                print out, error
                if error:
                    msg = error
                    print msg
                    jmsg = msg_para_json('F', 'ERR0060', msg)
                    return (jmsg)
                elif out:
                    msg = 'ETIQUETA IMPRESA CORRECTAMENTE...'
                    print msg
    
            elif modelo.startswith('DG860'):
                print 'MODELO: DG860'
                comando = Popen("CMD /C copy test_label.txt " + puertoCOM, stdout=PIPE, stderr=PIPE)
                out, error = comando.communicate()
                print out, error
                if error:
                    msg = error
                    print msg
                    jmsg = msg_para_json('F', 'ERR0060', msg)
                    return (jmsg)
                elif out:
                    msg = 'ETIQUETA IMPRESA CORRECTAMENTE...'
                    print msg
            
            elif modelo.startswith('TG862'):
                print 'MODELO: TG862'
                comando = Popen("CMD /C copy test_label.txt " + puertoCOM, stdout=PIPE, stderr=PIPE)
                out, error = comando.communicate()
                print out, error
                if error:
                    msg = error
                    print msg
                    jmsg = msg_para_json('F', 'ERR0060', msg)
                    return (jmsg)
                elif out:
                    comando = Popen("CMD /C copy wifi_label.txt " + puertoCOM, stdout=PIPE, stderr=PIPE)
                    out, error = comando.communicate()
                    print out, error
                    if error:
                        msg = error
                        print msg
                        jmsg = msg_para_json('F', 'ERR0060', msg)
                        return (jmsg)
                    elif out:
                        msg = 'ETIQUETA IMPRESA CORRECTAMENTE...'
                        print msg
    
            elif modelo.startswith('DG2470'):
                    print 'MODELO: DG2470'
                    comando = Popen("CMD /C copy test_label.txt " + puertoCOM, stdout=PIPE, stderr=PIPE)
                    out, error = comando.communicate()
                    print out, error
                    if error:
                        msg = error
                        print msg
                        jmsg = msg_para_json('F', 'ERR0060', msg)
                        return (jmsg)
                    elif out:
                        msg = 'ETIQUETA IMPRESA CORRECTAMENTE...'
                        print msg
    
            jmsg = msg_para_json('P')
            return (jmsg)
            
        except Exception, e:
            jmsg = msg_para_json('F', 'ERR0060', str(e))
            return (jmsg)                   
    def Falla (self,msg):

        
        self.lblShowMSG.setText(msg)
        self.guardar_logs(msg)
        self.btnStart.setText('I N I C I A R')                  
        self.iniciarPrueba = False
        self.lblShowMSG.setStyleSheet("background-color: orange")
        
        return
    def fecha_hora_actual(self,f=None, h=None):
        result = {}
        #localtime = time.asctime( time.localtime(time.time()) )
        if f is None:
            hoy = datetime.date.today()
        else:
            hoy = f
        #print "esta es la hora proporcionada", h
        #print "'" + str(hoy) + "'"
        
        horaactual =  time.strftime("%H%M%S",time.localtime(time.time()))
        #fechaactual = str(datetime.datetime.now().date()) + " "
        horaActual = time.strftime("%H:%M:%S",time.localtime(time.time()))
        #print horaActual
        fechaActual = hoy.strftime("%b %d %Y")
        #print fechaActual 
        ahoy = hoy.strftime("%m%d%Y")
        result['formato1'] = ahoy + horaactual
        #print result['formato1']
        result['formato2'] = fechaActual #+ " " + horaActual  
        #print result['formato2']
        result['formato3'] = datetime.date.today().strftime("%Y-%m-%d")
        
        # Cambio de formato de fecha hora para High-Jump
        horaActual = time.strftime("%H%M",time.localtime(time.time()))
        ahora = hoy.strftime("%Y%m%d")
        
        result['formato4'] = ahora + horaActual
        
        if h is not None:
            #print ahora + h.strftime("%H%M")
            result['formato5'] = ahora + h.strftime("%H%M")
        
        result['formato6'] = hoy.strftime("%d-%b-%y").upper()
        
        return (result)
    
    def PruebaCancelada (self):
        
        self.btnStart.setText('I N I C I A R')
        msg = ' ***  PRUEBA CANCELADA...  ****\n'
        self.lblShowMSG.setText(msg)
        self.guardar_logs(msg)
        self.iniciarPrueba = False
        self.lblShowMSG.setStyleSheet("background-color: orange")
        return 
    
    def Verificar_formatoTSN (self,TSNcapturado):
        
        result = 'P'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        
        try:
            if len(str(TSNcapturado)) != 15:
                msg = 'FORMATO DE NUMERO DE TSN INCORRECTO...'
                result = "F"
                Errorcode = 'ERROR 0101'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del TSN'
                retvalue ["Result"] = result
                self.Falla(msg)
                                             
            else:
                msg = 'NUMERO DE TSN INTRODUCIDO: ' + str(self.TSNcapturado)
                self.guardar_logs(msg)
        except:
            result = "F"
            Errorcode = 'ERROR_0101'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del TSN'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        return (retvalue)
    
    def Verificar_formatoMAC (self,MACcapturado):
        print MACcapturado
        result = 'P'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        
        try:
            if len(str(MACcapturado)) != 12:
                msg = 'FORMATO DE NUMERO DE MAC1 INCORRECTO...'
                result = "F"
                Errorcode = 'ERROR_0102'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del MAC'
                retvalue ["Result"] = result
                self.Falla(msg)
                                             
            else:
                msg = 'NUMERO DE MAC INTRODUCIDO: ' + str(MACcapturado)
                self.guardar_logs(msg)
                
        except:
            result = "F"
            Errorcode = 'ERROR_0102'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del MAC'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        #print retvalue    
        return (retvalue) 
    def Verificar_formatoSKU (self,SKUcapturado):

        print SKUcapturado
        result = 'P'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        
        try:
            if len(str(SKUcapturado)) != 6:
                msg = 'FORMATO DE NUMERO DE SKU INCORRECTO...'
                result = "F"
                Errorcode = 'ERROR 0102'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del SKU'
                retvalue ["Result"] = result
                self.Falla(msg)
                                             
            else:
                msg = 'NUMERO DE MAC INTRODUCIDO: ' + str(SKUcapturado)
                self.guardar_logs(msg)
                
        except:
            result = "F"
            Errorcode = 'ERROR_0102'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del SKU'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        #print retvalue    
        return (retvalue)
    def Verificar_formatoHOST (self,HostSNcapturado):
        print HostSNcapturado
        result = 'P'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        
        try:
            if len(str(HostSNcapturado)) != 12:
                msg = 'FORMATO DE HOST SN INCORRECTO...'
                result = "F"
                Errorcode = 'ERROR_0125'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del HOST SN'
                retvalue ["Result"] = result
                self.Falla(msg)
                                             
            else:
                msg = 'NUMERO DE HOST INTRODUCIDO: ' + str(HostSNcapturado)
                self.guardar_logs(msg)
                
        except:
            result = "F"
            Errorcode = 'ERROR_0125'
            ErrorDescription = 'Ha ocurrido un Error con la rutina de Verificar Formato del HOST SN'
        
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription
        return (retvalue)
    '''                      
    def conexion_telnet(self):     ######################## CONEXION PARA REALIZAR PRUEBAS FUNCIONALES  ######################
        
        result = 'F'
        Errorcode = 'X'
        ErrorDescription = 'X'
        retvalue = {}
        
        try:
    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 65533 Exitosa'
            self.guardar_logs (msg)
            output= tn.read_very_eager()
            time.sleep(2)
                     
            print output
           
            print 'HDMI & AUDIO Video Test'
            
            time.sleep(0.5)
            msg = 'ENVIANDO COMANDO :  ipclient 192.168.2.3 80 eth0 http HDMI1.ts 0x00777777'
            self.guardar_logs(msg)
            tn.write('ipclient 192.168.2.3 80 eth0 http HDMI1.ts 0x00777777\n')
            time.sleep(0.5)
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(0.5)
            msg = 'REALIZANDO PRUEBA DE VIDEO Y AUDIO HDMI'
            self.lblShowMSG.setText(msg)
            msg2 = 'HDMI TEST'
           #self.lblShowMSG_2.setText(msg2)
            
            self.tblResultado.setItem(0,0, QTableWidgetItem(msg2))
            self.tblResultado.resizeColumnsToContents()
            
            self.guardar_logs(msg)
            
            HDMIOK = QtGui.QMessageBox.question(self, 'HDMI AUDIO & VIDEO!',"Se Muestra Video HDMI y Audio?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if HDMIOK == QtGui.QMessageBox.No:
                msg = 'PRUEBA DE VIDEO Y AUDIO HDMI FALLO...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                msg2 = 'FAILED'
               #self.lblShowMSG_3.setText(msg2)
               #self.lblShowMSG_3.setStyleSheet("background-color: red")
                
                self.tblResultado.setItem(0,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(0,1).setBackground(QtGui.QColor(220, 00, 00))
                
                tn.write('ipclient disable')
                self.lblShowMSG.repaint()
                Errorcode = 'ERROR_0105'
                ErrorDescription = 'La unidad Tiene Problemas con el Puerto HDMI'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['HDMI_Test']= result
                self.Fallo()
                return (retvalue)
            
            msg = 'PRUEBA DE VIDEO Y AUDIO HDMI EXITOSA...'
            self.guardar_logs(msg)
            msg2 = 'PASSED'

            self.tblResultado.setItem(0,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(0,1).setBackground(QtGui.QColor(00,245,00))
            time.sleep(0.5)
            self.Informacion_DB['HDMI_Test']= 'P'
            msg2 = 'OPTICAL AUDIO TEST'
            self.tblResultado.setItem(1,0, QTableWidgetItem(msg2))
            msg = 'REALIZANDO PRUEBA DE AUDIO OPTICO'
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.repaint()
            self.guardar_logs(msg)
            
            OPTICALAUDIO = QtGui.QMessageBox.question(self, 'OPTICAL AUDIO!',"La Unidad Tiene Salida de Audio Optico?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if OPTICALAUDIO == QtGui.QMessageBox.No:
                
                msg = 'PRUEBA DE AUDIO OPTICO FALLO...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                msg2 = 'FAILED'
                self.tblResultado.setItem(1,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(1,1).setBackground(QtGui.QColor(220, 00, 00))
                tn.write('ipclient disable')
                msg = 'ENVIANDO COMANDO :    ipclient disable '
                self.guardar_logs (msg)
                msg = 'Video Stream Deshabilitado '
                self.guardar_logs (msg)
                time.sleep(2)
                self.lblShowMSG.repaint()
               #self.lblShowMSG_5.repaint()
                self.output = tn.read_very_eager()
                print repr(self.output)
                Errorcode = 'ERROR_0106'
                ErrorDescription = 'La unidad Tiene Problemas con el Puerto de Audio Optico'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['OPTICALAUDIO_Test']= result 
                self.Fallo()
                return (retvalue)
                         
            msg2 = 'PASSED'
            self.tblResultado.setItem(1,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(1,1).setBackground(QtGui.QColor(00,245, 00))
            msg = 'PRUEBA DE AUDIO OPTICO EXITOSA...'
            self.guardar_logs(msg)
           #self.lblShowMSG_5.repaint()
            """
            Boton = QtGui.QMessageBox.information(self, 'IR Test!',"Presione las teclas CH + y CH- ", QtGui.QMessageBox.Ok)
            self.Boton_IR = tn.read_very_eager()
            print repr(self.Boton_IR)
            
            Boton2 = QtGui.QMessageBox.information(self, 'Remote Finder Test!',"Presione el Boton Remote Finder ", QtGui.QMessageBox.Ok)
            self.Boton_Finder = tn.read_very_eager()
            print repr(self.Boton_Finder)
            """
            tn.write('ipclient disable \n')
            msg = 'ENVIANDO COMANDO :    ipclient disable '
            self.guardar_logs (msg)
            msg = 'Video Stream Deshabilitado '
            self.guardar_logs (msg)
            result = "P"
            time.sleep(2)
            self.Informacion_DB['OPTICAL_AUDIO_Test']= result
            self.output = tn.read_very_eager()
            print repr(self.output)
            self.lblShowMSG.repaint()
            Bluetooth= QtGui.QMessageBox.information(self, 'Bluetooth Test!',"!!!!Asegurece de Incializar el Dispositivo Bluetooth!!!!", QtGui.QMessageBox.Ok)  
#####################   Prueba de Bluetooth  ##############################
            time.sleep(0.5)
            msg = 'REALIZANDO PRUEBA DE BLUETOOTH...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            msg2 = 'BLUETOOTH TEST'
            self.tblResultado.setItem(2,0, QTableWidgetItem(msg2))
            self.lblShowMSG.repaint()
            print 'Bluetooth Init'
            msg = 'ENVIANDO COMANDO :    bt init'
            self.guardar_logs (msg)
            tn.write ('bt init \n')
            time.sleep(5)
            self.output = tn.read_very_eager()
            msg = 'Respuesta de Inicializacion de Bluetooth '
            self.guardar_logs (msg)
          
            print repr(self.output)
                                        
            BTSuccess= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>BT INIT ','\n\r')
            print BTSuccess ['valor']
            print BTSuccess ['result']
                  
            if BTSuccess ['valor'] is 'SUCCESS':
                    msg = 'INICIALIZACION DE BLUETOOTH EXITOSA...'
                    self.guardar_logs(msg)
                   
            else:                     
                    msg = 'INICIALIZACION DE BLUETOOTH FALLO...'
                    self.guardar_logs(msg)
                   
            time.sleep(1)
            print 'Searching Device'
            msg = 'ENVIANDO COMANDO :    bt e4:22:a5:f0:22:22 '
            self.guardar_logs (msg)
            msg = 'Buscando Dispositivo Bluetooth'
            self.guardar_logs (msg)
            #tn.write ('bt e4:22:a5:f0:22:22 \n')
            retResult =self. read_config('BLUETOOTH_INFO')
            MAC = retResult ['mac']
            if retResult['result'] == "F":
                return(retResult)
            print MAC
            tn.write ('bt '+ MAC +'\n')
            time.sleep(26)
            self.output = tn.read_very_eager()
            print repr(self.output)
            BTSuccess= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>BT test ',',')
            print BTSuccess ['valor']
            print BTSuccess ['result']
            btresult = BTSuccess ['valor']
            print btresult
            print repr(self.output)
            #BTRSSI= self.verificar_cadena(self.output, 'BT test PASS, ','\n\r')
            BTRSSI= self.verificar_cadena(self.output, ',','\n\r')
            print BTRSSI ['valor']
            print BTRSSI ['result']
            btresultRSSI = BTRSSI ['valor']
            print BTRSSI ['valor']
            
            if btresult == 'FAIL ':
                msg2 = 'FAILED'
                self.tblResultado.setItem(2,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(2,1).setBackground(QtGui.QColor(220, 00, 00))
                msg = 'PRUEBA DE BLUETOOTH FALLO...'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0107'
                ErrorDescription = 'La unidad Tiene Problemas con el Bluetooth'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['BLUETOOTH_Test']= (btresult + '  ' + BTRSSI ['valor'])
                self.Fallo()
                return (retvalue)
            
            msg2 = 'PASSED'
            self.tblResultado.setItem(2,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(2,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE BLUETOOTH EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['BLUETOOTH_Test']=  (btresult + '  ' + BTRSSI ['valor']) 
            msg = 'ENVIANDO COMANDO :    bt uninit'
            self.guardar_logs (msg)                        
            print 'Bluetooth Uninit'
            tn.write ('bt uninit \n')
            time.sleep(4)                    
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(1)
                          
#####################  Prueba de MoCA 1150 MHz  ##############################
            msg = 'REALIZANDO PRUEBA DE MoCA 1150 MHz...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.repaint()
            msg2 = 'MoCA 1150 MHz TEST'
            self.tblResultado.setItem(3,0, QTableWidgetItem(msg2))
            print 'MoCA Test 1150'
            msg = 'ENVIANDO COMANDO :    mocaset 1150 0 (0 = Normal Mode) '
            self.guardar_logs (msg)
            tn.write('mocaset 1150 0 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            print "Getting MoCA Rate Value"
            time.sleep(10)
            msg = 'ENVIANDO COMANDO :    mocaget '
            self.guardar_logs (msg)
            tn.write('mocaget \n')
            time.sleep(2)
            self.output = tn.read_very_eager()
            msg = self.output
            self.guardar_logs (msg)
            print repr(self.output)
            self.lblShowMSG.repaint()
            MoCAget1150 = self.verificar_cadena(self.output, 'FXN-MTC-RESP>>Freq=1150, link=1,phyrate=','\n\r')
            print MoCAget1150 ['valor']
            print MoCAget1150 ['result']
            ratevalue = MoCAget1150 ['valor']
            print ratevalue
            print type (ratevalue)
                    
                    
            if MoCAget1150 ['result'] is 'F':
                msg2 = 'FAILED'
                self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(3,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1150 MHz FALLO...'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0108'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1150_Test']= result
                self.Fallo()
                return (retvalue)
            
            numero = int (ratevalue)
            print type (numero)
            
            if numero < 530:
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(3,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1150 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0108'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1150_Test']= result
                self.Informacion_DB['MoCA1150_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            print "Es Mayor"
            msg2 = 'PASSED'
            self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(3,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE MoCA 1150 MHz EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['MoCA1150_Test']= 'P'
            self.Informacion_DB['MoCA1150_Baud_Rate']= numero 
                                            
            print 'Stop MoCA 1150'
            time.sleep(1)
            msg = 'ENVIANDO COMANDO :    mocaset 1150 6 (6 = Stop MoCA) '
            self.guardar_logs (msg)
            tn.write('mocaset 1150 6 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(1)
                   
                  
#####################  Prueba de MoCA 1600 MHz  ##############################                    
            msg = 'REALIZANDO PRUEBA DE MoCA 1600 MHz...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.repaint()
            msg2 = 'MoCA 1600 MHz TEST'
            self.tblResultado.setItem(4,0, QTableWidgetItem(msg2))
            self.lblShowMSG.repaint()
                    
            print 'MoCA Test 1600'
            msg = 'ENVIANDO COMANDO :    mocaset 1600 0 (0 = Normal Mode) '
            self.guardar_logs(msg)
            tn.write('mocaset 1600 0 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            print "Getting MoCA Rate Value"
            time.sleep(8)
            msg = 'ENVIANDO COMANDO :    mocaget'
            self.guardar_logs (msg)
            tn.write('mocaget \n')
            time.sleep(2)
            self.output = tn.read_very_eager()
            msg = self.output
            self.guardar_logs (msg)
            print repr(self.output)
                    
            MoCAget1600= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>Freq=1600, link=1,phyrate=','\n\r')
            print MoCAget1600 ['valor']
            print MoCAget1600 ['result']
            ratevalue = 0
            ratevalue = MoCAget1600 ['valor']
            print ratevalue
            print type (ratevalue)
                    
            if MoCAget1600 ['result'] is 'F':
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(4,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1600 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0109'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1600 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1600_Test']= result
                self.Informacion_DB['MoCA1600_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            numero = int (ratevalue)
            print type (numero)
            if numero < 530:
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(4,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1600 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0109'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1600_Test']= result
                self.Informacion_DB['MoCA1600_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            print "Es Mayor"
            msg2 = 'PASSED'
            self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(4,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE MoCA 1600 MHz EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['MoCA1600_Test']= 'P'
            self.Informacion_DB['MoCA1600_Baud_Rate']= numero             
            print 'Stop MoCA 1600'
            time.sleep(1)
            msg = 'ENVIANDO COMANDO :    mocaset 1600 6 (6 = Stop MoCA) '
            self.guardar_logs (msg)
            tn.write('mocaset 1600 6 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            #print 'Iniciando Incremento'
           #self.paso()
                    
        except Exception, Error:
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 65533  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)
    '''                          
    def conexionSTC_telnet(self):  ######################## CONEXION PARA VERIFICACION DE INFORMACION INTERNA ##################

        
        result = 'F'
        Errorcode = None
        ErrorDescription = None
        prueba = ''
        retvalue = {}
        
        try:
            time.sleep(2)
            tn = telnetlib.Telnet ('192.168.2.200',49152)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 49152 Exitosa'
            self.guardar_logs (msg)
            output= tn.read_very_eager()
            print output
            msg = '\n'+ output
            self.guardar_logs (msg)  
            tn.write('getmac\n')
            time.sleep(2)
            msg = tn.read_very_eager()
            print msg
            self.guardar_logs (msg)
            self.output = msg
            print repr(self.output)
            self.lblShowMSG.repaint()
            msg = 'VERIFICANDO INFORMACION INTERNA'
            self.guardar_logs (msg)
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.repaint()
            #InfoInterna = {}
            
            MAC1_Get = self.verificar_cadena(self.output, '\nMAC6_MoCA     : ','\n')
            print MAC1_Get ['valor']
            print MAC1_Get ['result']
            MAC1 = MAC1_Get['valor'].replace(' ',"")
            msg = MAC1
            self.guardar_logs (msg)
            
            MAC2_Get = self.verificar_cadena(self.output, '\nMAC2_Ethernet : ','\n')
            print MAC2_Get ['valor']
            print MAC2_Get ['result']
            MAC2 = MAC2_Get['valor'].replace(' ',"")    
            msg =MAC2
            self.guardar_logs (msg)
                   
            self.lblShowMSG.repaint()
            time.sleep(2)
            tn.write('repairtcdinfo GetInfo 3\n')
            time.sleep(8)
            msg = tn.read_very_eager()
            
            self.guardar_logs (msg)
            self.output = msg
            print repr(self.output)
            TSN_Get = self.verificar_cadena(self.output, '|','|')
            print TSN_Get ['valor']
            print TSN_Get ['result']
            msg = TSN_Get ['valor']
            self.guardar_logs (msg)
            
            ####Solo aplica para IP900 ###
            
            HOST_SN_Get = self.verificar_cadena(self.output,TSN_Get ['valor'],'|0x')
            print HOST_SN_Get['valor']
            print HOST_SN_Get['result']
            HOST_SN = HOST_SN_Get['valor'].replace('|',"")
            msg = HOST_SN
            self.guardar_logs (msg)
            self.Informacion_DB['HostSN_Interno']= HOST_SN
        
            TCD_Info_Current = self.verificar_cadena(self.output, 'CONNECT\n' , '@OK\n\n')
            print TCD_Info_Current ['valor']
            print TCD_Info_Current ['result']
            self.Informacion_DB['TCD_Info_Current'] = TCD_Info_Current ['valor']
            
            prueba = TCD_Info_Current ['valor'] [0:3251]
            print len(prueba)
            print prueba
            
            self.Informacion_DB['TCD_Info_Current'] = prueba
            
            
            if TCD_Info_Current ['result'] is 'F':
                msg ='No se Obtuvo Informacion del TCD_Info'
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)                
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                #result = "F"
                Errorcode = 'ERROR_0103'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return (retvalue)
                    
            self.Informacion_DB['TSN_Interno']= TSN_Get['valor']
            self.Informacion_DB['MAC1_Interno']= MAC1
            self.Informacion_DB['MAC2_Interno']= MAC2
            
            self.lblShowMSG.repaint()
            
            if TSN_Get ['result'] is 'F':
                msg ='No se Obtuvo Informacion del TCD_Info'
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)                
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                #result = "F"
                Errorcode = 'ERROR_0103'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return (retvalue)
            
            if TSN_Get['valor'] != self.TSN_Scan:
                   
                msg ='EL TSN INTERNO ' + TSN_Get['valor'] + ' ES DIFERENTE AL PROPORCIONADO '+ self.TSN_Scan
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)
                self.lblscan.setText('   TSN Interno :  ' + TSN_Get['valor'])
                self.lblscan.setStyleSheet("background-color: red")                  
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                #result = "F"
                Errorcode = 'ERROR_0103'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return (retvalue)
            
            msg = 'EL NUMERO DE SERIE DE TIVO INTERNO ' + TSN_Get['valor'] + ' ES IGUAL AL PROPORCIONADO ' + self.TSN_Scan
            print msg
            self.guardar_logs(msg)        
            
            if MAC1 != self.MAC1_Scan:
                msg = 'El MAC ADDRESS 1 INTERNO ' + MAC1 + ' ES DIFERENTE AL PROPORCIONADO' + self.MAC1_Scan
                print msg
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)
                self.lblscan.setText('   MAC1 Interno :  ' +MAC1)
                self.lblscan.setStyleSheet("background-color: red")
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')     
                #result = "F"
                Errorcode = 'ERROR_0103'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return(retvalue)
               
            msg = 'EL NUMERO DE MAC1 INTERNO  '+MAC1 +'  ES IGUAL AL PROPORCIONADO '+ self.MAC1_Scan
            print msg
            self.guardar_logs(msg)
             
            if MAC2 != self.MAC2_Scan:
                msg = 'El MAC ADDRESS 1 INTERNO ' + MAC2 + ' ES DIFERENTE AL PROPORCIONADO' + self.MAC2_Scan
                print msg 
                self.lblShowMSG.setStyleSheet("background-color: red") 
                self.lblShowMSG.setText(msg)
                self.lblscan.setText('   MAC2 Interno : ' + MAC2)
                self.lblscan.setStyleSheet("background-color: red")
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                #result = "F"
                Errorcode = 'ERROR_0103'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription 
                return (retvalue)
            
            result = "P"
            msg = 'EL NUMERO DE MAC1 INTERNO  '+MAC2 +'  ES IGUAL AL PROPORCIONADO '+ self.MAC2_Scan    
            print msg
            self.guardar_logs(msg)
                        
            if self.comboBox.currentText() == 'IP900':
                if HOST_SN != self.HostSN_Scan:
                    msg = 'El HOST SN INTERNO ' + HOST_SN + ' ES DIFERENTE AL PROPORCIONADO ' + self.HostSN_Scan
                    print msg 
                    self.lblShowMSG.setStyleSheet("background-color: red") 
                    self.lblShowMSG.setText(msg)
                    self.lblscan.setText('   MAC2 Interno : ' + MAC2)
                    self.lblscan.setStyleSheet("background-color: red")
                    self.guardar_logs(msg)
                    self.btnStart.setText('I N I C I A R')   
                    #result = "F"
                    Errorcode = 'ERROR_0103'
                    ErrorDescription = 'Ha ocurrido un Error con la rutina de Comparacion de Informacion Interna'
                    retvalue ["Result"] = result                  
                    retvalue ["Error_Code"] = Errorcode
                    retvalue ["Error_Description"]= ErrorDescription 
                    return (retvalue)
                
                #self.Informacion_DB['HostSN_Interno']= HOST_SN
                result = "P"
                msg = 'EL NUMERO DE HOST SN INTERNO  '+HOST_SN +'  ES IGUAL AL PROPORCIONADO '+ self.HostSN_Scan    
                print msg
                self.guardar_logs(msg)
                                   
        except Exception,Error:
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 49152  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)
    
    def Incremento_TSN (self):     ######################## CONEXION PARA INCREMENTO DE TSN ##################
        
        result = 'F'
        Errorcode = None
        ErrorDescription = None
        retvalue = {}
        
        try:
            time.sleep(2)
            tn = telnetlib.Telnet ('192.168.2.200',49152)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 49152 Exitosa'
            self.guardar_logs (msg)
            output= tn.read_very_eager()
            print output
            msg = 'INCREMENTANDO NUMERO DE TSN'
            self.guardar_logs (msg)
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.repaint() 
################ Configurar Hora & Fecha ##################################            
            result1= {}
    
            hoy = datetime.date.today ()
            Hora_Minutos = time.strftime("%H%M", time.localtime(time.time()))
            fechaactual =hoy.strftime("%b %d %Y")
            fechaActual =hoy.strftime("%Y")
            
            Mes_Dia = hoy.strftime ("%m%d")
            
            result1['formato'] = Mes_Dia + Hora_Minutos + fechaActual

            tn.write('settime ' +result1['formato'] + '\n')
    
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
            print repr(self.output)
###################### INCREMENTANDO TSN ###########################
            time.sleep(2)
            tn.write('repairtcdinfo IncrementTSN 3\n')
            time.sleep(8)
            msg = tn.read_very_eager()
            print msg
            self.output = msg
            print repr(self.output)
            
            Increment_TSN = self.verificar_cadena(self.output, 'repairtcdinfo IncrementTSN 3\n@ERROR','\n\n')
            print Increment_TSN ['valor']
            print Increment_TSN ['result']   
    
            if Increment_TSN ['result'] is 'P':
                msg ='NO SE INCREMENTO EL NUMERO DE TSN'
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)                
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                    
                Errorcode = 'ERROR_0110'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de Incremento de TSN'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return (retvalue)        
############Obteniendo Informacion del nuevo TCD Info  ##############################
            msg = 'OBTENIENDO NUEVA INFORMACION'
            self.guardar_logs (msg)
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.repaint()
            print 'SI PUDO HACER EL INCREMENTO'
            time.sleep(2)
            tn.write('repairtcdinfo GetInfo 3\n')
            time.sleep(8)
            msg = tn.read_very_eager()
            print msg
            self.guardar_logs (msg)
            self.output = msg
            print repr(self.output)
            
            New_TSN_Get = self.verificar_cadena(self.output, '\n07|','|')
            print New_TSN_Get ['valor']
            print New_TSN_Get ['result']
            
           
            TCD_Info_New = self.verificar_cadena(self.output, 'CONNECT\n' , '@OK\n\n')
            print TCD_Info_New ['valor']
            print TCD_Info_New ['result']
            '''
            self.Informacion_DB['TCD_Info_New'] = TCD_Info_New ['valor']
            '''
            
            prueba = TCD_Info_New['valor'] [0:3251]
            print len(prueba)
            print prueba
            
            self.Informacion_DB['TCD_Info_New'] = prueba
            
            if TCD_Info_New ['result'] is 'F':
                msg ='No se Obtuvo Informacion del TCD_Info'
                self.lblShowMSG.setStyleSheet("background-color: red")
                self.lblShowMSG.setText(msg)                
                self.guardar_logs(msg)
                self.btnStart.setText('I N I C I A R')   
                #result = "F"
                Errorcode = 'ERROR_0110'
                ErrorDescription = 'Ha ocurrido un Error con la rutina de TCD_Info_New'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                return (retvalue)
                    
            self.Informacion_DB['TSN_New']= New_TSN_Get ['valor']
            
            result = "P"
            msg = 'EL NUEVO NUMERO DE TSN ES   :' + New_TSN_Get ['valor']  
            print msg
            self.guardar_logs(msg) 
                               
        except Exception,Error:
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 49152  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue) 
              
    def paso(self):
        if self.iniciarPrueba is True:
                            
            self.lblShowMSG.setStyleSheet("background-color: rgb(0,255,0)")
            msg = 'LA PRUEBA FUE EXITOSA.... \nPRUEBA FINALIZADA'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.iniciarPrueba = False
            self.btnStart.setText('I N I C I A R')
                        
                
        else:
            msg = 'LA PRUEBA NO SE HA INICIADO...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.setStyleSheet("background-color: orange")

        return
      
    def Fallo(self):
        if self.iniciarPrueba is True:
                            
            self.lblShowMSG.setStyleSheet("background-color: red")
            msg = 'LA PRUEBA NO FUE EXITOSA.... \nPRUEBA FINALIZADA'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.iniciarPrueba = False
            self.btnStart.setText('I N I C I A R')
                        
        else:
            msg = 'LA PRUEBA NO SE HA INICIADO...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.setStyleSheet("background-color: orange")

        #return
    def verificar_cadena (self, cadenaOriginal=None, palabraClave=None, palabraFinal=None): 
        
        result_msg = {}
        if cadenaOriginal is None:
            test = open('testString.txt', 'r')
            testLines = test.read()
            test.close()
        else:
            testLines = cadenaOriginal
        if palabraClave is None:
            cadena = 'WPS PIN                  - '
        else:
            cadena = palabraClave
    
        if palabraFinal is None:
            palabraFinal = '\r\n'
    
        pos_a = testLines.find(cadena)
        if pos_a == -1:
            result_msg['result'] = 'F'
            result_msg ['valor']= 'Palabra clave no se encontro'
            return (result_msg)
    
        #t = testLines[pos_a : pos_a + len(cadena)]
   
        pos_inicial = pos_a + len(cadena)
    
        fin_linea = testLines.find(palabraFinal,pos_inicial)
  
        if fin_linea == -1:
            result_msg ['result'] = 'F'
            result_msg ['valor']= 'Palabra final no se encontro'
            return (result_msg)
        
        e = testLines[pos_inicial: fin_linea]
        result_msg["result"]="P"
        result_msg['valor'] = e
        
        return (result_msg)
     
    def guardar_logs(self, msg):
        
        fechaactual = str(datetime.datetime.now().date()) + " "
        horaactual = time.strftime("%H:%M:%S", time.localtime(time.time())) + " "
        h_f = fechaactual + horaactual
        
        NombreArchivo =fechaactual + self.TSNcapturado
        logg = open(NombreArchivo + '.log', 'a' )
        
        #logg = open('test_db_class.log', 'a' )
        logg.write('\n' + f_h() + msg)
        logg.close()
        #self.logviewer.appendPlainText(self.f_h() + mesg)
        print f_h() +  msg    
        self.txtLog.appendPlainText(h_f + msg)
        
        return
    def Verificacion_Audio_Video (self):
        
        result = 'F'
        Errorcode = 'X'
        ErrorDescription = 'X'
        retvalue = {}
        
        try:    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 65533 Exitosa'
            self.guardar_logs (msg)
            output= tn.read_very_eager()
            time.sleep(2)
                     
            print output
           
            print 'HDMI & AUDIO Video Test'
            
            time.sleep(0.5)
            msg = 'ENVIANDO COMANDO :  ipclient 192.168.2.3 80 eth0 http HDMI1.ts 0x00777777'
            self.guardar_logs(msg)
            tn.write('ipclient 192.168.2.3 80 eth0 http HDMI1.ts 0x00777777\n')
            time.sleep(0.5)
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(0.5)
            msg = 'REALIZANDO PRUEBA DE VIDEO Y AUDIO HDMI'
            self.lblShowMSG.setText(msg)
            msg2 = 'HDMI TEST'
            
            self.tblResultado.setItem(0,0, QTableWidgetItem(msg2))
            self.tblResultado.resizeColumnsToContents()
            
            self.guardar_logs(msg)
            
            HDMIOK = QtGui.QMessageBox.question(self, 'HDMI AUDIO & VIDEO!',"Se Muestra Video HDMI y Audio?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if HDMIOK == QtGui.QMessageBox.No:
                msg = 'PRUEBA DE VIDEO Y AUDIO HDMI FALLO...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                msg2 = 'FAILED'              
                self.tblResultado.setItem(0,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(0,1).setBackground(QtGui.QColor(220, 00, 00))
                tn.write('ipclient disable')
                self.lblShowMSG.repaint()
                Errorcode = 'ERROR_0105'
                ErrorDescription = 'La unidad Tiene Problemas con el Puerto HDMI'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['HDMI_Test']= result
                self.Fallo()
                return (retvalue)
            
            msg = 'PRUEBA DE VIDEO Y AUDIO HDMI EXITOSA...'
            self.guardar_logs(msg)
            msg2 = 'PASSED'

            self.tblResultado.setItem(0,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(0,1).setBackground(QtGui.QColor(00,245,00))
            time.sleep(0.5)
            self.Informacion_DB['HDMI_Test']= 'P'
            msg2 = 'OPTICAL AUDIO TEST'
            self.tblResultado.setItem(1,0, QTableWidgetItem(msg2))
            msg = 'REALIZANDO PRUEBA DE AUDIO OPTICO'
            self.lblShowMSG.setText(msg)
            self.lblShowMSG.repaint()
            self.guardar_logs(msg)
            
            OPTICALAUDIO = QtGui.QMessageBox.question(self, 'OPTICAL AUDIO!',"La Unidad Tiene Salida de Audio Optico?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            
            if OPTICALAUDIO == QtGui.QMessageBox.No:
                
                msg = 'PRUEBA DE AUDIO OPTICO FALLO...'
                self.lblShowMSG.setText(msg)
                self.guardar_logs(msg)
                msg2 = 'FAILED'
                self.tblResultado.setItem(1,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(1,1).setBackground(QtGui.QColor(220, 00, 00))
                tn.write('ipclient disable')
                msg = 'ENVIANDO COMANDO :    ipclient disable '
                self.guardar_logs (msg)
                msg = 'Video Stream Deshabilitado '
                self.guardar_logs (msg)
                time.sleep(2)
                self.lblShowMSG.repaint()
                self.output = tn.read_very_eager()
                print repr(self.output)
                Errorcode = 'ERROR_0106'
                ErrorDescription = 'La unidad Tiene Problemas con el Puerto de Audio Optico'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['OPTICALAUDIO_Test']= result 
                self.Fallo()
                return (retvalue)
                         
            msg2 = 'PASSED'
            self.tblResultado.setItem(1,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(1,1).setBackground(QtGui.QColor(00,245, 00))
            msg = 'PRUEBA DE AUDIO OPTICO EXITOSA...'
            self.guardar_logs(msg)
          
            tn.write('ipclient disable \n')
            msg = 'ENVIANDO COMANDO :    ipclient disable '
            self.guardar_logs (msg)
            msg = 'Video Stream Deshabilitado '
            self.guardar_logs (msg)
            result = "P"
            time.sleep(2)
            self.Informacion_DB['OPTICAL_AUDIO_Test']= result
            self.output = tn.read_very_eager()
            print repr(self.output)
            self.lblShowMSG.repaint() 
            
        except Exception, Error:
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 65533  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)
    def Verificacion_Bluetooth(self):
        result = 'P'
        Errorcode = 'X'
        ErrorDescription = 'X'
        retvalue = {}
        
        try:    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 65533 Exitosa'
            self.guardar_logs (msg)
            Bluetooth= QtGui.QMessageBox.information(self, 'Bluetooth Test!',"!!!!Asegurece de Incializar el Dispositivo Bluetooth!!!!", QtGui.QMessageBox.Ok)  
#####################   Prueba de Bluetooth  ##############################
            time.sleep(0.5)
            msg = 'REALIZANDO PRUEBA DE BLUETOOTH...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            msg2 = 'BLUETOOTH TEST'
            self.tblResultado.setItem(2,0, QTableWidgetItem(msg2))
            self.lblShowMSG.repaint()
            print 'Bluetooth Init'
            msg = 'ENVIANDO COMANDO :    bt init'
            self.guardar_logs (msg)
            tn.write ('bt init \n')
            time.sleep(5)
            self.output = tn.read_very_eager()
            msg = 'Respuesta de Inicializacion de Bluetooth '
            self.guardar_logs (msg)
          
            print repr(self.output)
                                        
            BTSuccess= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>BT INIT ','\n\r')
            print BTSuccess ['valor']
            print BTSuccess ['result']
                  
            if BTSuccess ['valor'] is 'SUCCESS':
                    msg = 'INICIALIZACION DE BLUETOOTH EXITOSA...'
                    self.guardar_logs(msg)
            '''         
            else:                     
                    msg = 'INICIALIZACION DE BLUETOOTH FALLO...'
                    self.guardar_logs(msg)
            '''         
            time.sleep(1)
            print 'Searching Device'
            msg = 'ENVIANDO COMANDO :    bt e4:22:a5:f0:22:22 '
            self.guardar_logs (msg)
            msg = 'Buscando Dispositivo Bluetooth'
            self.guardar_logs (msg)
            #tn.write ('bt e4:22:a5:f0:22:22 \n')
            retResult =self. read_config('BLUETOOTH_INFO')
            MAC = retResult ['mac']
            if retResult['result'] == "F":
                return(retResult)
            print MAC
            tn.write ('bt '+ MAC +'\n')
            time.sleep(26)
            self.output = tn.read_very_eager()
            print repr(self.output)
            BTSuccess= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>BT test ',',')
            print BTSuccess ['valor']
            print BTSuccess ['result']
            btresult = BTSuccess ['valor']
            print btresult
            print repr(self.output)
            #BTRSSI= self.verificar_cadena(self.output, 'BT test PASS, ','\n\r')
            BTRSSI= self.verificar_cadena(self.output, ',','\n\r')
            print BTRSSI ['valor']
            print BTRSSI ['result']
            btresultRSSI = BTRSSI ['valor']
            print BTRSSI ['valor']
            
            if btresult == 'FAIL ':
                msg2 = 'FAILED'
                self.tblResultado.setItem(2,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(2,1).setBackground(QtGui.QColor(220, 00, 00))
                msg = 'PRUEBA DE BLUETOOTH FALLO...'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0107'
                ErrorDescription = 'La unidad Tiene Problemas con el Bluetooth'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['BLUETOOTH_Test']= (btresult + '  ' + BTRSSI ['valor'])
                self.Fallo()
                return (retvalue)
            
            msg2 = 'PASSED'
            self.tblResultado.setItem(2,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(2,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE BLUETOOTH EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['BLUETOOTH_Test']=  (btresult + '  ' + BTRSSI ['valor']) 
            msg = 'ENVIANDO COMANDO :    bt uninit'
            self.guardar_logs (msg)                        
            print 'Bluetooth Uninit'
            tn.write ('bt uninit \n')
            time.sleep(4)                    
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(1)
            
        except Exception, Error:
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 65533  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)
    
    def Verificacion_MOCA1150(self):
        result = 'P'
        Errorcode = 'X'
        ErrorDescription = 'X'
        retvalue = {}
        
        try:    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 65533 Exitosa'
            self.guardar_logs (msg)
            #####################  Prueba de MoCA 1150 MHz  ##############################
            msg = 'REALIZANDO PRUEBA DE MoCA 1150 MHz...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.repaint()
            msg2 = 'MoCA 1150 MHz TEST'
            self.tblResultado.setItem(3,0, QTableWidgetItem(msg2))
            print 'MoCA Test 1150'
            msg = 'ENVIANDO COMANDO :    mocaset 1150 0 (0 = Normal Mode) '
            self.guardar_logs (msg)
            tn.write('mocaset 1150 0 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            print "Getting MoCA Rate Value"
            time.sleep(10)
            msg = 'ENVIANDO COMANDO :    mocaget '
            self.guardar_logs (msg)
            tn.write('mocaget \n')
            time.sleep(2)
            self.output = tn.read_very_eager()
            msg = self.output
            self.guardar_logs (msg)
            print repr(self.output)
            self.lblShowMSG.repaint()
            MoCAget1150 = self.verificar_cadena(self.output, 'FXN-MTC-RESP>>Freq=1150, link=1,phyrate=','\n\r')
            print MoCAget1150 ['valor']
            print MoCAget1150 ['result']
            ratevalue = MoCAget1150 ['valor']
            print ratevalue
            print type (ratevalue)
                            
            if MoCAget1150 ['result'] is 'F':
                msg2 = 'FAILED'
                self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(3,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1150 MHz FALLO...'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0108'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1150_Test']= result
                self.Fallo()
                return (retvalue)
            
            numero = int (ratevalue)
            print type (numero)
            
            if numero < 530:
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(3,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1150 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0108'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1150_Test']= result
                self.Informacion_DB['MoCA1150_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            print "Es Mayor"
            msg2 = 'PASSED'
            self.tblResultado.setItem(3,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(3,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE MoCA 1150 MHz EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['MoCA1150_Test']= 'P'
            self.Informacion_DB['MoCA1150_Baud_Rate']= numero 
                                            
            print 'Stop MoCA 1150'
            time.sleep(1)
            msg = 'ENVIANDO COMANDO :    mocaset 1150 6 (6 = Stop MoCA) '
            self.guardar_logs (msg)
            tn.write('mocaset 1150 6 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            time.sleep(1)
        except Exception, Error:
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 65533  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)
    def Verificacion_MOCA1600(self):
        result = 'P'
        Errorcode = 'X'
        ErrorDescription = 'X'
        retvalue = {}
        
        try:    
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            msg = 'Conexion IP: 192.168.2.200 Puerto 65533 Exitosa'
            self.guardar_logs (msg)
#####################  Prueba de MoCA 1600 MHz  ##############################                    
            msg = 'REALIZANDO PRUEBA DE MoCA 1600 MHz...'
            self.lblShowMSG.setText(msg)
            self.guardar_logs(msg)
            self.lblShowMSG.repaint()
            msg2 = 'MoCA 1600 MHz TEST'
            self.tblResultado.setItem(4,0, QTableWidgetItem(msg2))
            self.lblShowMSG.repaint()
                    
            print 'MoCA Test 1600'
            msg = 'ENVIANDO COMANDO :    mocaset 1600 0 (0 = Normal Mode) '
            self.guardar_logs(msg)
            tn.write('mocaset 1600 0 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
            print "Getting MoCA Rate Value"
            time.sleep(8)
            msg = 'ENVIANDO COMANDO :    mocaget'
            self.guardar_logs (msg)
            tn.write('mocaget \n')
            time.sleep(2)
            self.output = tn.read_very_eager()
            msg = self.output
            self.guardar_logs (msg)
            print repr(self.output)
                    
            MoCAget1600= self.verificar_cadena(self.output, 'FXN-MTC-RESP>>Freq=1600, link=1,phyrate=','\n\r')
            print MoCAget1600 ['valor']
            print MoCAget1600 ['result']
            ratevalue = 0
            ratevalue = MoCAget1600 ['valor']
            print ratevalue
            print type (ratevalue)
                    
            if MoCAget1600 ['result'] is 'F':
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(4,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1600 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0109'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1600 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1600_Test']= result
                #self.Informacion_DB['MoCA1600_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            numero = int (ratevalue)
            print type (numero)
            if numero < 530:
                print "Valor es Menor" 
                msg2 = 'FAILED'
                self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
                self.tblResultado.item(4,1).setBackground(QtGui.QColor(220,00, 00))
                msg = 'PRUEBA DE MoCA 1600 MHz FALLO...EL VALOR ES MENOR'
                self.guardar_logs(msg)
                result = 'F'
                Errorcode = 'ERROR_0109'
                ErrorDescription = 'La unidad Tiene Problemas de MoCA 1150 MHz'
                retvalue ["Result"] = result                  
                retvalue ["Error_Code"] = Errorcode
                retvalue ["Error_Description"]= ErrorDescription
                self.Informacion_DB['MoCA1600_Test']= result
                self.Informacion_DB['MoCA1600_Baud_Rate']= numero
                self.Fallo()
                return (retvalue)
                
            print "Es Mayor"
            msg2 = 'PASSED'
            self.tblResultado.setItem(4,1, QtGui.QTableWidgetItem(msg2)) 
            self.tblResultado.item(4,1).setBackground(QtGui.QColor(00, 245, 00))
            msg = 'PRUEBA DE MoCA 1600 MHz EXITOSA...'
            self.guardar_logs(msg)
            self.Informacion_DB['MoCA1600_Test']= 'P'
            self.Informacion_DB['MoCA1600_Baud_Rate']= numero             
            print 'Stop MoCA 1600'
            time.sleep(1)
            msg = 'ENVIANDO COMANDO :    mocaset 1600 6 (6 = Stop MoCA) '
            self.guardar_logs (msg)
            tn.write('mocaset 1600 6 \n')
            time.sleep(1)
            self.output = tn.read_very_eager()
            print repr(self.output)
          
        except Exception, Error:
            tn = telnetlib.Telnet ('192.168.2.200',65533)
            time.sleep(2)
            result = "F"
            Errorcode = 'ERROR_0100' 
            ErrorDescription = 'Ha ocurrido un Error con la rutina de conexion al puerto 65533  ' + str(Error)
            self.guardar_logs (ErrorDescription)
            retvalue ["Result"] = result
            msg = 'Verifique la Conexion del Cable Ethernet'
            self.Falla(msg)
            
        retvalue ["Result"] = result                  
        retvalue ["Error_Code"] = Errorcode
        retvalue ["Error_Description"]= ErrorDescription 
                 
        return (retvalue)          
    def conexion_telnet(self):     ######################## CONEXION PARA REALIZAR PRUEBAS FUNCIONALES  ######################
      
        retvalue = {}
        
        retResult=self.Verificacion_Audio_Video()
        print retResult
        
        if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                #retVal = self._process_guardar_datos(self.Informacion_DB)
                retvalue ["Result"] = retResult ["Result"]               
                retvalue ["Error_Code"] = retResult ["Error_Code"]
                retvalue ["Error_Description"]= retResult ["Error_Description"]
                #print retVal
                return (retvalue)
            
        retResult=self.Verificacion_Bluetooth()
        print retResult
        
        if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                #retVal = self._process_guardar_datos(self.Informacion_DB)
                retvalue ["Result"] = retResult ["Result"]               
                retvalue ["Error_Code"] = retResult ["Error_Code"]
                retvalue ["Error_Description"]= retResult ["Error_Description"]
                #print retVal
                return (retvalue)
           
        retResult=self.Verificacion_MOCA1150()
        print retResult
        retResult['Result'] == "P"
        if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                #retVal = self._process_guardar_datos(self.Informacion_DB)
                retvalue ["Result"] = retResult ["Result"]               
                retvalue ["Error_Code"] = retResult ["Error_Code"]
                retvalue ["Error_Description"]= retResult ["Error_Description"]
                #print retVal
                return (retvalue) 
           
        retResult=self.Verificacion_MOCA1600()
        print retResult
        
        if retResult['Result'] == "F":
                self.Informacion_DB['Failure_Code']= retResult ["Error_Code"]
                self.Informacion_DB['Failure_Description']= retResult ["Error_Description"]
                self.Informacion_DB['Result'] = retResult ["Result"]
                #retVal = self._process_guardar_datos(self.Informacion_DB)
                retvalue ["Result"] = retResult ["Result"]               
                retvalue ["Error_Code"] = retResult ["Error_Code"]
                retvalue ["Error_Description"]= retResult ["Error_Description"]
                #print retVal
                return (retvalue)
         
        retvalue ["Result"] = retResult ["Result"]               
        retvalue ["Error_Code"] = retResult ["Error_Code"]
        retvalue ["Error_Description"]= retResult ["Error_Description"]
                   
        return (retvalue)           
app = QtGui.QApplication(sys.argv)
miVentana = principal(None)
miVentana.show()
app.exec_()