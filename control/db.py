#import oracledb
import cx_Oracle
import streamlit as st 

def get_connection():
    #return oracledb.connect(**st.secrets.db_credentials)
    return cx_Oracle.connect(user=st.secrets.db_credentials.user, password=st.secrets.db_credentials.password,dsn=st.secrets.db_credentials.dsn)
    

# conn = get_connection()
# cursor = conn.cursor()
# cursor.execute("SELECT name FROM users where id = 2")
# res = cursor.fetchone()
# cursor.close()
# conn.close()
# print(res)