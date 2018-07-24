'''
Created on Jun 14, 2018

@author: Administrator
'''
import MySQLdb
 
DB_HOST = 'localhost' 
DB_USER = 'root' 
DB_PASS = 'ip90x_db' 
DB_NAME = 'ip90x_tbl' 
 #ip90user
def run_query(query=''): 
    datos = [DB_HOST, DB_USER, DB_PASS, DB_NAME] 
 
    conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
    cursor = conn.cursor()         # Crear un cursor 
    cursor.execute(query)          # Ejecutar una consulta 
 
    if query.upper().startswith('SELECT'): 
        data = cursor.fetchall()   # Traer los resultados de un select 
    else: 
        conn.commit()              # Hacer efectiva la escritura de datos 
        data = None 
 
    cursor.close()                 # Cerrar el cursor 
    conn.close()                   # Cerrar la conexin 
 
    return data