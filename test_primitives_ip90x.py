'''
Created on May 10, 2018

@author: Jose Mendoza

'''


import ConfigParser
import collections
import json
import datetime
import time
import xml.etree.cElementTree as ET
import traceback
import sys
import socket
from subprocess import *

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

def fecha_hora_actual():
    result = {}
    #localtime = time.asctime( time.localtime(time.time()) )
    hoy = datetime.date.today()
    horaactual =  time.strftime("%H%M%S",time.localtime(time.time()))
    #fechaactual = str(datetime.datetime.now().date()) + " "
    horaActual = time.strftime("%H:%M:%S",time.localtime(time.time()))
    #print horaActual
    fechaActual = hoy.strftime("%b %d %Y")
    #print fechaActual 
    hoy = hoy.strftime("%m%d%Y")
    result['formato1'] = hoy+horaactual
    #print result['formato1']
    result['formato2'] = fechaActual + " " + horaActual  
    #print result['formato2']
    
    return (result)

def _process_guardar_datos(GuardarDatos):
        db = MXDBAccess()
        retResult = db.db_connection()
        print "Status de conexion a la base de datos"
        print retResult
        #print GuardarDatos
        retVal = db.insert_data(GuardarDatos)
        
        #print retVal
        #print GuardarDatos
        #print 'Limpiando datos'
        #GuardarDatos = _clear_data(GuardarDatos)
        #print GuardarDatos
        return
    
def principal_store_data():
    retVal = read_config('STATION_INFO')
    datos = UnitDetail()
    GuardarDatos = datos.guardarDatos
    GuardarDatos = {'MAC2_Interno': '20F19E03B4EB', 'TSN_Scanned': 'A95068D7C92599D', 'MAC1_Scanned': '20F19E03B4ED', 'MAC1_Interno': '20F19E03B4ED', 'TSN_Interno': 'A95068D7C92599D',\
        'MAC2_Scanned': '20F19E03B4EB', 'SKU_Scanned': 'RA9500', "TSN_New": "X", "Model": "X", "Station": "X", "Slot": "1", "Test_Station": "X", "Result": "P", "Failure_Description": "X", \
        "TCD_Info_Current": "07|A95068D7C92599D|M91734EH0149|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F5300FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCAC2B9B9A8A0A28DC28770D898E514EF870C24E6C724EFAF22FF2751015FEE75924C8C43B3857D89467C7D3A596C822CF0BCE3FBFC1FFB2339FC5A62642C60108669CF6EC74E1432E7A4769FD5505E230B612DF6488C378E849F645E3E4F19FE4DDDC5B196F5831C90AE514421D8467A7B15969630C9BDFD3916049CE152B00EACE95B6AB0303F5262D07A54E5DAF9C024CABD9D084E23F673E5A6FF35F9C1A5099F63E51A6251F7F0865891E8FF2ED456E5614317DB73170D8DC0BD2DB2D8EE580E55F6D1E3AEB39BE88C59554A1C1650E530ED1CD965E9885448BFD9E3E84673FECBCE35F13DA183FD27099C8F76A2BE3ADA9F9116888F384D2C95700|0x54E956EF051F4139353036384437433932353939442F4D39313733344548303134392F4500FC6D31EC427BC465B09E15B7F63713FA178A6BA9AB5ADD09C3331096A4B7452C73020DD5CA25840DFDC22ECE8AB0C7D222A199239E44A83096409825E42632BBB62B97EDDCB4A1814BD89B8DC44CF59ECBBD8EAEF6C6CC732F6058561DD0A44803A1941FD37748C1C7CED56E1A28ADA500AFF2FA7E3263C54E4DEEC50F87F6CC28ECBA5425B5D8999265DE822DC0A07A7F1940E054B6E4CF9CD4D87786FBB666F8DE7FC2C65D389BBBB3CE4F4A2A216FEBF553783FD87E61399DC2F0F0D28F83E76760C40AE275B4DB49AC733CB9F525B9D5595AFB7C9272364E4E19CD2925DBC190BF7852AE46E06E2AAB95351EE72E6BB5E6DC4949B324FD46E767D2FC2803DAC9A6A996C3D44EE302FE9DBB33552723AFB167D4F713E7ED5EF8514F971E431C01FAC51B0402AE80063DAD2FA8BC2F4A7860DECC3DEE08EABC9D0026676851F7C2278323C4224C4FBE2F0CA19BEBC238337F3B70691B7131205D8E18663C8F0B3D7D38A82098587F443460A31A76F6D719CB0B2D0CB369085635785907AE949E3FD34B271672D1EE25A5C3E57A915DB80DE2D0E445057F69F37BD83ACA93744083A9DF2CCCC04CA90A80244F097EC9F839E1AB74AC24199A2712B388BCC2424A71B5A4559F1CBDC8D5298A1397B250ED12E971FEFE5B32F1703969974FBD989D2F5453783000FBD7EB3C8957695CB1F69A9B057BFB9C2CEEA7FCBAE3B25120E509E0A765F7B91EE26DE8A9994852A75DF4682DA0AE3A85ED6D0488E7D4E4AE708331A2CA8E5EEFB761518F35A92803D8E0C8A9EF12B400EFE12DF1B8B9BED5E42306FFB9884AB8EBD7888FB72C2D6C313EEEEE855A67E949D54D58837ABAC5274FB703799342D74FA4D823E9239E68DF1E2DCCA356E4EC33D3728767ED786FF2032A1DADDFAB0D8AED9A8DA0A16E919DE079200261016FFCCBBC19283302D393F7CA0FC1C31330E0FEB4C256C6193B58BD2DDB7FA3F2151AA7D76DED3389C0D05B63C7A8E773D128F85C763485B5AEA3513C9C72615C0D047311E48AF03000B22D922D8FEAFCBD33676C213AB568E8FC4160941AAA6900|0000F01156AB9CCA|1241C2FD", \
        "TCD_Info_New": "X"}
    
    GuardarDatos['Test_Station'] = retVal['test_station']
    #GuardarDatos['Model'] = 'X'
    GuardarDatos['Station'] = retVal['station']
    retVal = _process_guardar_datos(GuardarDatos)
    print retVal
    
    return

def consulta_tsn(tsn_number):
    db = MXDBAccess()
    retResult = db.db_connection()
    #print "Status de conexion a la base de datos"
    #print retResult
    
    # VERIFICAR SI HAY UN ERROR AL CONECTARSE A LA BASE DE DATOS
    if retResult['result'] == "F":
        #print retResult['errorCode']
        #print retResult['errorDescription']
        #print retResult['failureReason']
        return (retResult)
    
    buscar_sn = db.consultar_sn_(tsn_number)
    
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
        result_msg['tcdInfo'] = buscar_sn['Datos'][0]['TCD_Info_Current']
        
    
    return (result_msg)

def ip90x_build_xml(tcdinfo, birthdate=None):
    try:
        fechas = fecha_hora_actual()
        birthdate = fechas['formato2']
        root = ET.Element("manufacturingdatastore")
        doc = ET.SubElement(root, "hardware")
        
        #ET.SubElement(doc, "birthdate").text = "Aug 28 2010 19:02:00"

        ET.SubElement(doc, "birthdate").text = birthdate
        #ET.SubElement(doc, "tcdinfo").text = "sdasdsadsadasdasdsadsadasdasdadasd"
        ET.SubElement(doc, "tcdinfo").text = tcdinfo
        #ET.ElementTree(root).write(noteFile, encoding="utf-8", xml_declaration=True)
        
        #write(file, encoding="us-ascii", xml_declaration=None, default_namespace=None, method="xml")
        hoy = fecha_hora_actual()['formato1']
        tree = ET.ElementTree(root)
        tree.write("Contec_Matamoros" + "_TCDKeys_" + hoy + ".xml", encoding="utf-8", xml_declaration=True, default_namespace=None)
    except Exception, e:
        #print e
        errCode = "ERR1050"
        log_msg = traceback.format_exc()
        print log_msg
        #print log_msg

def abrirImpresora(modelo, opciones=None):
    result_msg = {}
    try:
        retResult = read_config('PRINT_INFO')
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

def crear_archivo(modelo, infoImprimir, opciones=None):
    jmsg = {}
    
    try:
        if modelo.startswith("IP901"):
            print "CREANDO ARCHIVO DE ETIQUETA PARA MODELO: " + modelo
            f = open('ip90x_label.txt', 'w')
            terminacionCampo = "^FS"
            inicioCampo = "^FD"
            terminacionLinea = "\n"
            comandoInicial = '^XA' + terminacionLinea
            labelHome = "50,400"
            configurarHome = '^LH' + labelHome + terminacionCampo + terminacionLinea
            fontSize = "40,30"
            fontName = "E:AVE000.FNT"
            f.write(comandoInicial)
            f.write(configurarHome)
            
            f.write("^FO0,100^A@N," + fontSize + "," + fontName + inicioCampo + "TSN: " + infoImprimir["tsn"] + terminacionCampo + terminacionLinea)
            f.write("^FO0,125^GB450,0,34"+ terminacionCampo + terminacionLinea)
            f.write("^FR^FO25,125^BY2,1.48^BCN,34,N,N,N" + inicioCampo + infoImprimir["tsn"] + terminacionCampo + terminacionLinea)
            
            f.write("^FO0,180^A@N," + fontSize + "," + fontName + inicioCampo + "MAC1: " + infoImprimir["mac1"] + terminacionCampo + terminacionLinea)
            f.write("^FO0,205^GB381,0,34" + terminacionCampo + terminacionLinea)
            f.write("^FR^FO25,205^BY2,1.48^BCN,34,N,N,N" + inicioCampo + infoImprimir["mac1"] + terminacionCampo + terminacionLinea)
            
            f.write("^FO0,260^A@N," + fontSize + "," + fontName + inicioCampo + "MAC2: " + infoImprimir["mac2"] + terminacionCampo + terminacionLinea)
            f.write("^FO0,285^GB381,0,34" + terminacionCampo + terminacionLinea)
            f.write("^FR^FO25,285^BY2,1.48^BCN,34,N,N,N" + inicioCampo + infoImprimir["mac2"] + terminacionCampo + terminacionLinea)
            
            f.write("^FO0,340^A@N," + fontSize + "," + fontName + inicioCampo + "SKU: " + infoImprimir["sku"] + terminacionCampo + terminacionLinea)
            f.write("^FO0,365^GB250,0,34"  + terminacionCampo + terminacionLinea)
            f.write("^FR^FO25,365^BY2,1.48^BCN,34,N,N,N" + inicioCampo + infoImprimir["sku"] + terminacionCampo + terminacionLinea)
            
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

def imprimirIP(modelo, opciones=None):
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
            retVal = abrirImpresora(modelo)
            if retVal['result'] == "F":
                return(retVal)
            sock = retVal['socket']
            f = open('ip90x_label.txt', 'r')
            zplCMDIDS = f.read()
            f.close()
            print >> sys.stderr, 'Enviando: \n "%s"' % zplCMDIDS
            sock.sendall(zplCMDIDS)
            sock.close()
        
        jmsg = msg_para_json('P')
        return (jmsg)
    
    except Exception, e:
        print e
        jmsg = msg_para_json('F', 'ERR0062', str(e))
        return (jmsg)

def imprimirEtiqueta(modelo, modo, opciones=None):
    if modo == 'SERIAL':
        retVal = imprimirSerial(modelo, opciones)
        return (retVal)
        
    elif modo == "IP":
        retVal = imprimirIP(modelo, opciones)
        return (retVal)

def imprimirSerial(modelo, opciones=None):
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


if __name__ == '__main__':
    
    ### ***************************************************************************************** ###
    modelo                  = "IP901"
    modoImpresion           = "IP"
    datosImprimir           = {}
    datosImprimir['tsn']    = "A9503B519B506E5"
    datosImprimir['mac1']   = "20F19ED69551"
    datosImprimir['mac2']   = "20F19ED6954F"
    datosImprimir['sku']    = "RA9500"

    print "Corriendo la rutina crear_archivo..."
    retVal = crear_archivo(modelo, datosImprimir)
    print retVal
    print "Corriendo la rutina imprimirEtiqueta..."
    retVal = imprimirEtiqueta(modelo, modoImpresion)
    print retVal
    
    
    ### ***************************************************************************************** ###
    '''
    #print fecha_hora_actual()
    retResult = consulta_tsn('A954CB0A1E7CF0E')
    print retResult
    
    retVal = ip90x_build_xml(retResult['tcdInfo'])
    print retVal
    '''

