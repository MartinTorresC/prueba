'''
Created on May 5, 2018

@author: Jose Mendoza
'''


import ConfigParser
import collections
import json
import datetime
import time

from db_class import UnitDetail, MXDBAccess, msg_para_json, guardar_logs, f_h


def read_config(section):
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

def _process_guardar_datos(Informacion_DB):
        db = MXDBAccess()
        retResult = db.db_connection()
        print "Status de conexion a la base de datos"
        print retResult
        #print GuardarDatos
        retVal = db.insert_data(Informacion_DB)
        
        #print retVal
        #print GuardarDatos
        #print 'Limpiando datos'
        #GuardarDatos = _clear_data(GuardarDatos)
        #print GuardarDatos
        return
    
def principal_store_data():
    retVal = read_config('STATION_INFO')
    datos = UnitDetail()
    Informacion_DB = datos.guardarDatosRTDS
    
    
    Informacion_DB = { 
                        "TSN"                 : 'A95068D7C92599D',
                        "RSA"                 : '645656',
                        #"Receivig_Date"       : '',
                        "SKU"                 : 'RA950P',
                        #"Packing_Date"        : '',
                        "Status"              : 'Celda',
                        "XML_Info"            : 'X',
                        "TSN_New"             : 'X',}
    
    Informacion_DB['Test_Station'] = retVal['test_station']
    Informacion_DB['Model'] = 'X'
    Informacion_DB['Station'] = retVal['station']
    retVal = _process_guardar_datos(Informacion_DB)
    print retVal
    
    return

def consulta_tsn(tsn_number):
    db = MXDBAccess()
    retResult = db.db_connection()
    print "Status de conexion a la base de datos"
    print retResult
    buscar_sn = db.consultar_sn_(tsn_number)
    print buscar_sn
    print len(buscar_sn['Datos'])
    if buscar_sn['result'] == "F":
        print 'No se encontro el numero de TSN'
    else:
        print 'Numero de serie encontrado'
        print buscar_sn['Datos'][0]['Hora'], buscar_sn['Datos'][0]['Fecha'] 
        print buscar_sn['Datos'][0]['TCD_Info_Current']
    
    return


if __name__ == '__main__':
    
    
    
    retResult = principal_store_data()
    print retResult
    
    #retResult = consulta_tsn('A95068D7C92599D')
    #print retResult
    
    
    