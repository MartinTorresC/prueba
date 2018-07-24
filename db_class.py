'''
Created on Jun 30, 2017

@author: Jose Mendoza
'''
import sys;
import MySQLdb;
import json
import datetime
import collections
import logging
import time
import md5
import ConfigParser

from ConfigParser import SafeConfigParser


from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy import schema, types, create_engine
from sqlalchemy import and_
    
def guardar_logs(mesg):
        logg = open('test_db_class.log', 'a' )
        logg.write('\n' + f_h() + mesg)
        logg.close()
        #self.logviewer.appendPlainText(self.f_h() + mesg)
        print f_h() +  mesg
        return
    
def f_h():
        #localtime = time.asctime( time.localtime(time.time()) )
        horaactual =  time.strftime("%H:%M:%S",time.localtime(time.time())) + " "
        fechaactual = str(datetime.datetime.now().date()) + " "
        return (fechaactual+horaactual)


def msg_para_json(result, errorCode=None, errorDescription=None, failure_reason='CAUSA DE ERROR NO ASIGNADA'):
    #failureReason = 'Error desconocido'
    jmsg = collections.OrderedDict()
    #jmsg = {}
    jmsg['result'] = result
    if result != "P":
        if errorCode is None or len(errorCode) == 0:
            errorCode = "ERR0000"
        if errorDescription is None or len(errorDescription) == 0:
            errorDescription = "DESCRIPCION DE ERROR NO ASIGNADA"
        jmsg['errorCode'] = errorCode
        jmsg['errorDescription'] = errorDescription
        jmsg['failureReason'] = failure_reason
        #l = guardar_logs(json.dumps(jmsg))
    
    return (jmsg)

def read_cmodems_db_info(configFile):
    try:
        config = ConfigParser.RawConfigParser()
        fp = open(configFile, 'r')
        config.readfp(fp, configFile)
        db_server_ip = config.get("CMODEMS_DB_INFO", "IP_HOST")
        db_server_db = config.get("CMODEMS_DB_INFO", "DB_DB")
        db_server_table = config.get("CMODEMS_DB_INFO", "DB_TABLE")
        db_server_user = config.get("CMODEMS_DB_INFO", "DB_USER")
        db_server_pass = config.get("CMODEMS_DB_INFO", "DB_PASS")
        return (True, db_server_ip, db_server_db, db_server_table, db_server_user, db_server_pass)
    except:
        db_server_ip     = ''
        db_server_db     = ''
        db_server_table = ''
        db_server_user     = ''
        db_server_pass     = ''
        return (False, db_server_ip, db_server_db, db_server_table, db_server_user, db_server_pass)

class MXDBAccess(object):
    def __init__(self):
        self.usedb = True
        self.db = None      # Contiene una instancia del objeto base de datos
        self.datos = None   # Contien el recordset de datos extraidos de la tabla
        #self.guardarDatos = {}
        
    def init_guardar_datos(self):
        
        self.guardarDatos = {"Fecha"                : 'X',
                            "Hora"                  : 'X',
                            "Slot"                  : 'X',
                            "Result"                : 'X',
                            "Failure_Code"          : 'X',
                            "Failure_Description"   : 'X',
                            "Model"                 : 'X',
                            "TSN_Scanned"           : 'X',
                            "MAC1_Scanned"          : 'X',
                            "MAC2_Scanned"          : 'X',
                            "SKU_Scanned"           : 'X',
                            "TSN_Interno"           : 'X',
                            "MAC1_Interno"          : 'X',
                            "MAC2_Interno"          : 'X',
                            "TSN_New"               : 'X',
                            "TCD_Info_Current"      : 'X',
                            "TCD_Info_New"          : 'X',
                            "Station"               : 'X',
                            "Test_Station"          : 'X',
                            "user"                  : 'X'}
        
        self.guardarDatosRTDS = {"Fecha"              : 'X',
                                "Hora"                : 'X',
                                #"TSN"                 : 'X',
                                #"RSA"                 : 'X',
                                #"Receivig_Date"       : 'X',
                                #"SKU"                 : 'X',
                                #"Packing_Date"        : 'X',
                                #"Status"              : 'X',
                                "XML_Info"            : 'X',
                                "TSN_New"             : 'X',}
    
    def db_connection(self, tabla=None):
        #Hacer la conexion a la base de datos
        #Linea Original
        #db = create_engine('mysql+mysqldb://edemsamodems:contec@' + db_host + '/modems_db')
        #print tabla
        #leerConfig = read_cmodems_db_info("config.conf")
        leerConfig = read_cmodems_db_info("config_ip90.conf")
        #print leerConfig
        if leerConfig[0] is True:
            db_host     = leerConfig[1]
            db_db       = leerConfig[2]
            if tabla is None:
                db_table    = leerConfig[3]
            else:
                db_table    = tabla
            #print db_table
            db_user     = leerConfig[4]
            db_pass     = leerConfig[4]
        else:
            msg = "ERROR AL LEER ARCHIVO DE CONFIGURACION PARA OBETENER PARAMETROS DE LA BASE DE DATOS...\nPRUEBA ABORTADA"
            #self.db = None
            #self.datos = None
            err_code = "ERR0031"
            jmsg = msg_para_json("F", err_code, msg, msg)
            return (jmsg)
    
        #db = create_engine('mysql+mysqldb://' + db_user + ':' + db_pass + '@' + db_host + '/' + db_db)
        #print db_table
        try:
            #print db_host, db_db, db_table
            #self.db = create_engine('mysql+mysqldb://edemsamodems:contec@' + db_host + '/' + db_db)
            self.db = create_engine('mysql+mysqldb://ip90user:password321@' + db_host + '/' + db_db)
            self.db.echo = False  # Try changing this to True and see what happens
            metadata = schema.MetaData(self.db)
            print "si se conecto"
            #Linea Original
            #datos = Table('arris_tbl', metadata, autoload=True)
            self.datos = Table(db_table, metadata, autoload=True)
            print "despues de la conexion a la tabla"
            jmsg = msg_para_json("P")
        
        except Exception, e:
            print e
            print "Ha ocurrido el error", e
            frc = sys.exc_info()
            err_code = 'ERR0030'
            msg = 'Error al abrir o conectarse a la DB'
            jmsg = msg_para_json("F", err_code, msg, frc)
            #return (jmsg)
         
        return (jmsg)
    
    def consultar_SN_(self, s_number, tsa=None, tsp=None):
        #print tsa, tsp
        tested_ok_current_station   = False
        tested_ok_prev_station      = False
        result = "F"
        '''
        Para hacer un select segun los campos que se requieran
        '''
        
        #jmsg['Datos'] = []
        try:
            cursor_data = self.datos
            
            s = cursor_data.select(cursor_data.c.TSN == s_number).order_by(desc(cursor_data.c.idip90x_rcvd_tbl)) #.distinct(cursor_data.c.Serial_Scan)
            #cursor_data.
            rs = s.execute()
            #print rs
            '''
                fetchall te da la salida como diccionario
                fetchone te da la salida como una lista
            '''
            todas = rs.fetchall()           
            #print todas
            if todas:
                for renglon in todas:
                    print 'Encontre este primero', renglon['Fecha'], renglon['Hora'], renglon['TSN']
                    #if renglon['Test_Station'] == tsa and renglon['Result'] == 'P':
                    #    tested_ok_current_station = True
                    
                    #if renglon['Test_Station'] == tsp and renglon['Result'] == 'P':
                    #    tested_ok_prev_station = True
                    #print renglon['Test_Station']
                    #print renglon
                    #print 'Encontre este primero', renglon['Fecha'], renglon['Hora'], renglon['Serial_Scan']
                    #f = str(renglon['Fecha'])
                    #h = str(renglon['Hora'])
                    #pf = str(renglon['Result'])
                    #ts = str(renglon['Test_Station'])
                    #run(rs)
                    result = 'P'
                jmsg = msg_para_json(result)
                #jmsg['Result']  = result
                jmsg['Datos'] = todas
                
                
            else:
                result = 'F'
                errorCode = 'ERR00032'
                errorDescription = 'Numero de TSN no encontrado'
                failureReason = errorDescription
                jmsg = msg_para_json(result, errorCode, errorDescription, failureReason)
                jmsg['Datos'] = []
                return (jmsg)
        except:
            result = 'F'
            errorCode = 'ERR00033'
            errorDescription = 'Ha ocurrido el error'
            failureReason = sys.exc_info()
            jmsg = msg_para_json(result, errorCode, errorDescription, failureReason)
            jmsg['Datos'] = []
            return (jmsg)
        
        
    
        self.db.dispose()
        #jmsg = msg_para_json(result)
        
        #jmsg['tested_ok_current_station'] =  tested_ok_current_station
        #jmsg['tested_ok_prev_station'] =  tested_ok_prev_station
        
        return (jmsg)
     
    def consultar_sn_(self, s_number, tsa=None, tsp=None):
        #tsa = 'PRINT_LABEL'
        #tsp ='FUT'   
        #print tsa, tsp
        tested_ok_current_station   = False
        tested_ok_prev_station      = False
        result = "F"
        '''
        Para hacer un select segun los campos que se requieran
        '''
        
        #jmsg['Datos'] = []
        try:
            cursor_data = self.datos
            
            #s = cursor_data.select(cursor_data.c.TSN_Scanned == s_number).order_by(desc(cursor_data.c.id_ip90x)) #.distinct(cursor_data.c.Serial_Scan)
            #cursor_data.
            s = cursor_data.select(and_(cursor_data.c.TSN_Scanned == s_number,\
                                        cursor_data.c.Test_Station == tsp,\
                                        cursor_data.c.Result == 'P')).order_by(desc(cursor_data.c.id_ip90x)) #.distinct(cursor_data.c.Serial_Scan)
            rs = s.execute()
            #print rs
            '''
                fetchall te da la salida como diccionario
                fetchone te da la salida como una lista
            '''
            todas = rs.fetchall()           
            #print todas
            if todas:
                for renglon in todas:
                    print 'Encontre este primero', renglon['Fecha'], renglon['Hora'], renglon['TSN_Scanned']
                    
                    #if renglon['Test_Station'] == tsa and renglon['Result'] == 'P':
                    #    tested_ok_current_station = True
                    '''
                    if renglon['Test_Station'] == tsp and renglon['Result'] == 'P':
                        print "Este paso la prueba",renglon['Fecha'], renglon['Hora'], renglon['TSN_Scanned']
                        tested_ok_prev_station = True
                        result = 'P'
                        jmsg = msg_para_json(result)
                        jmsg['Datos'] = renglon
                        jmsg['passOK'] = tested_ok_prev_station
                        jmsg['Result']  = result
                                                
                        break
                    '''
                    result = 'P'
                    jmsg = msg_para_json(result)
                    jmsg['Datos'] = renglon
                    jmsg['passOK'] = tested_ok_prev_station
                    jmsg['Result']  = result
                    #print renglon['Test_Station']
                    #print renglon
                    #print 'Encontre este primero', renglon['Fecha'], renglon['Hora'], renglon['Serial_Scan']
                    #f = str(renglon['Fecha'])
                    #h = str(renglon['Hora'])
                    #pf = str(renglon['Result'])
                    #ts = str(renglon['Test_Station'])
                    #run(rs)
                    
                
                #jmsg['Result']  = result
                
                
            else:
                
                result = 'F'
                errorCode = 'ERR00032'
                errorDescription = 'Numero de TSN no encontrado'
                failureReason = errorDescription
                jmsg = msg_para_json(result, errorCode, errorDescription, failureReason)
                jmsg['Datos'] = []
                return (jmsg)
        except:
        
            result = 'F'
            errorCode = 'ERR00033'
            errorDescription = 'Ha ocurrido el error'
            failureReason = sys.exc_info()
            jmsg = msg_para_json(result, errorCode, errorDescription, failureReason)
            jmsg['Datos'] = []
            return (jmsg)
        
        
    
        self.db.dispose()
        #jmsg = msg_para_json(result)
        
        #jmsg['tested_ok_current_station'] =  tested_ok_current_station
        #jmsg['tested_ok_prev_station'] =  tested_ok_prev_station
        print tested_ok_prev_station
        #print jmsg
        return (jmsg)
      
    def insert_data(self, datosAguardar):
        #logger = logging.getLogger('MXCore')
        #Para insertar un registro en la tabla
        fecha = datetime.datetime.now().date()
        datosAguardar['Fecha'] = fecha
        
        #datosAguardar['Receiving_Date'] = fecha
        #datosAguardar['Packing_Date'] = fecha
        hora = datetime.datetime.now().time()
        datosAguardar['Hora'] = hora
        result = 'F'
        
        try:
            cursor_data = self.datos
            i=cursor_data.insert()
            i.execute(datosAguardar)
    
            self.db.dispose()
            result = 'P'
        except Exception, e:
            print sys.exc_info()
            log_msg = "Falla al insertar registro en la tabla"
            #logger.exception("Falla al insertar registro en la tabla")
            print log_msg
            log_msg = "Ha ocurrido el error: "
            print log_msg
            #logger.info("Ha ocurrido el error: ")
            log_msg = str(e) 
            #looger.info(e)
            print log_msg
            result = 'F'
            err_code = 'ERR00036'
            err_desc = 'Error al abrir o almacenar los datos en la tabla'
            frc = err_desc
            jmsg = msg_para_json(result, err_code, err_desc, frc)
            return (jmsg)
        
        jmsg = msg_para_json(result)
        return (jmsg)
    
                 
class UnitDetail(object):
    def __init__(self):
        #id_ip90x,datetime,Hora,Fecha,Slot,Result,Failure_Code,Failure_Description,Test_Station,Station,TSN_Scanned,MAC1_Scanned,MAC2_Scanned,SKU_Scanned,TSN_Interno,MAC1_Interno,MAC2_Interno,TSN_New
        '''
        {'MAC2_Interno': '20F19E03B4EB', 'TSN_Scanned': 'A95068D7C92599D', 'MAC1_Scanned': '20F19E03B4ED', 'MAC1_Interno': '20F19E03B4ED', 'TSN_Interno': 'A95068D7C92599D',\
        'MAC2_Scanned': '20F19E03B4EB', 'SKU_Scanned': 'RA9500', "TSN_New": "X", "Model": "X", "Station": "X", "Slot": "1", "Test_Station": "X", \
        "TCD_Info_Current": "07|A95068D7C92599D|M91734EH0149|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F5300FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCAC2B9B9A8A0A28DC28770D898E514EF870C24E6C724EFAF22FF2751015FEE75924C8C43B3857D89467C7D3A596C822CF0BCE3FBFC1FFB2339FC5A62642C60108669CF6EC74E1432E7A4769FD5505E230B612DF6488C378E849F645E3E4F19FE4DDDC5B196F5831C90AE514421D8467A7B15969630C9BDFD3916049CE152B00EACE95B6AB0303F5262D07A54E5DAF9C024CABD9D084E23F673E5A6FF35F9C1A5099F63E51A6251F7F0865891E8FF2ED456E5614317DB73170D8DC0BD2DB2D8EE580E55F6D1E3AEB39BE88C59554A1C1650E530ED1CD965E9885448BFD9E3E84673FECBCE35F13DA183FD27099C8F76A2BE3ADA9F9116888F384D2C95700|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F4500FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCBAE3B25120E509E0A765F7B91EE26DE8A9994852A75DF4682DA0AE3A85ED6D0488E7D4E4AE708331A2CA8E5EEFB761518F35A92803D8E0C8A9EF12B400EFE12DF1B8B9BED5E42306FFB9884AB8EBD7888FB72C2D6C313EEEEE855A67E949D54D58837ABAC5274FB703799342D74FA4D823E9239E68DF1E2DCCA356E4EC33D3728767ED786FF2032A1DADDFAB0D8AED9A8DA0A16E919DE079200261016FFCCBBC19283302D393F7CA0FC1C31330E0FEB4C256C6193B58BD2DDB7FA3F2151AA7D76DED3389C0D05B63C7A8E773D128F85C763485B5AEA3513C9C72615C0D047311E48AF03000B22D922D8FEAFCBD33676C213AB568E8FC4160941AAA6900|0000F01156AB9CCA|1241C2FD"}
        '''
        #print 'Me llamaron'
        #self.guardarDatos = collections.OrderedDict()
        self.guardarDatos = {"Fecha"                : 'X',
                            "Hora"                  : 'X',
                            "Slot"                  : 'X',
                            "Result"                : 'X',
                            "Failure_Code"          : 'X',
                            "Failure_Description"   : 'X',
                            "Model"                 : 'X',
                            "TSN_Scanned"           : 'X',
                            "MAC1_Scanned"          : 'X',
                            "MAC2_Scanned"          : 'X',
                            "SKU_Scanned"           : 'X',
                            "TSN_Interno"           : 'X',
                            "MAC1_Interno"          : 'X',
                            "MAC2_Interno"          : 'X',
                            "TSN_New"               : 'X',
                            "TCD_Info_Current"      : 'X',
                            "TCD_Info_New"          : 'X',
                            "Station"               : 'X',
                            "Test_Station"          : 'X',
                            "user"                  : 'X',
                            "HDMI_Test"             : 'X',
                            "OPTICAL_AUDIO_Test"    : 'X',
                            "BLUETOOTH_Test"        : 'X',
                            "MoCA1150_Test"         : 'X',
                            "MoCA1150_Baud_Rate"    : 'X',
                            "MoCA1600_Test"         : 'X',
                            "MoCA1600_Baud_Rate"    : 'X',}

        self.guardarDatosRTDS = {"Fecha"              : 'X',
                                "Hora"                : 'X',
                                "TSN"                 : 'X',
                                "RSA"                 : 'X',
                                "Receivig_Date"       : 'X',
                                "SKU"                 : 'X',
                                "Packing_Date"        : 'X',
                                "Status"              : 'X',
                                "XML_Info"            : 'X',
                                "TSN_New"             : 'X',}
        
#datos = UnitDetail()

#print datos.guardarDatos

#exit(0)



#-----------MAINT TEST ROUTINE ---------------
#*****COMENTARLA CUANDO SE TERMINE DE HACER LAS PRUEBAS ********


if __name__ == '__main__':
    '''
        Secuencia principal solo para probar los modulos
    '''
    
    datos = UnitDetail()
    t = read_cmodems_db_info("config_ip90.conf")
    #print t
    
    datos.guardarDatos = {'MAC2_Interno': '20F19E03B4EB', 'TSN_Scanned': 'A95068D7C92599D', 'MAC1_Scanned': '20F19E03B4ED', 'MAC1_Interno': '20F19E03B4ED', 'TSN_Interno': 'A956CB0A1E7CF0D',\
        'MAC2_Scanned': '20F19E03B4EB', 'SKU_Scanned': 'RA9500', "TSN_New": "X", "Model": "X", "Station": "X", "Slot": "1", "Test_Station": "X", "Result": "P", "Failure_Description": "X", \
        "TCD_Info_Current": "07|A95068D7C92599D|M91734EH0149|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F5300FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCAC2B9B9A8A0A28DC28770D898E514EF870C24E6C724EFAF22FF2751015FEE75924C8C43B3857D89467C7D3A596C822CF0BCE3FBFC1FFB2339FC5A62642C60108669CF6EC74E1432E7A4769FD5505E230B612DF6488C378E849F645E3E4F19FE4DDDC5B196F5831C90AE514421D8467A7B15969630C9BDFD3916049CE152B00EACE95B6AB0303F5262D07A54E5DAF9C024CABD9D084E23F673E5A6FF35F9C1A5099F63E51A6251F7F0865891E8FF2ED456E5614317DB73170D8DC0BD2DB2D8EE580E55F6D1E3AEB39BE88C59554A1C1650E530ED1CD965E9885448BFD9E3E84673FECBCE35F13DA183FD27099C8F76A2BE3ADA9F9116888F384D2C95700|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F4500FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCBAE3B25120E509E0A765F7B91EE26DE8A9994852A75DF4682DA0AE3A85ED6D0488E7D4E4AE708331A2CA8E5EEFB761518F35A92803D8E0C8A9EF12B400EFE12DF1B8B9BED5E42306FFB9884AB8EBD7888FB72C2D6C313EEEEE855A67E949D54D58837ABAC5274FB703799342D74FA4D823E9239E68DF1E2DCCA356E4EC33D3728767ED786FF2032A1DADDFAB0D8AED9A8DA0A16E919DE079200261016FFCCBBC19283302D393F7CA0FC1C31330E0FEB4C256C6193B58BD2DDB7FA3F2151AA7D76DED3389C0D05B63C7A8E773D128F85C763485B5AEA3513C9C72615C0D047311E48AF03000B22D922D8FEAFCBD33676C213AB568E8FC4160941AAA6900|0000F01156AB9CCA|1241C2FD", \
        "TCD_Info_New": "X"}
    
    db = MXDBAccess()
    retResult = db.db_connection()
    print "Status de conexion a la base de datos"
    print retResult
    #print datos.guardarDatos
    
    #retVal = db.insert_data(datos.guardarDatos)
    #print "Status de insertar a tabla"
    #print retVal
    #sys.exit(0)
    
    buscar_sn = db.consultar_sn_('A958CB0A1E7CF0C')
    print buscar_sn
    
    print len(buscar_sn['Datos'])
    print buscar_sn
    
    if buscar_sn['result'] == "F":
        print 'No se encontro el numero de TSN'
    else:
        print 'Numero de serie encontrado'
        print buscar_sn['Datos']['Hora'], buscar_sn['Datos']['Fecha'] 
        print buscar_sn['Datos']['TCD_Info_Current']
        print buscar_sn['Datos']['Result']
        print buscar_sn['Datos']['Test_Station']
        print buscar_sn['Datos']['TCD_Info_Current']
    '''    
    Actualizar = db.update_data('A95068D7C92599D')
    print len(Actualizar['Datos'])
    print Actualizar
    
    if Actualizar['result'] == "F":
        print 'No se encontro el numero de TSN'
    else:
        print 'Numero de serie encontrado'
        print Actualizar['Datos'][0]['Hora'], Actualizar['Datos'][0]['Fecha'] 
        print Actualizar['Datos'][0]['TCD_Info_Current']
    '''
    sys.exit(0)
    
    '''
    if retResult['result'] == "P":
        #print db.db
        #print db.datos
        buscar_sn = db.consultar_sn_('CBKB4E77B207471', 'FUT', 'FUT-PHONE')
        print buscar_sn
        if buscar_sn['result'] is not False:
            print 'Numero de serie encontrado'
        else:
            print 'No se encontro el numero de serie'
    
    datos = UnitDetail()
    #print datos.guardarDatos
    
    retVal = db.insert_data(datos.guardarDatos)
    
    print retVal
    
    '''
    
    exit(0)
    
    
    
    
    '''        
    
    db = MXDBAccess()
    
    #print db
    
    #print db.checkDUTSerial('CBKB4E77B207471')
    
    
    dut = db.getDUTBySerial('CBKB4E77B207471')
    
    print dut.serial_scanned
    print dut.model
    
    print dut.fecha
    print dut.hora
    print dut.snr32
    '''
    
    
    
    
    
    
    
    
