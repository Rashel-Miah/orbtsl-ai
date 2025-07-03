#from fastapi import HTTPException
from .db import get_connection
#import oracledb
import json

def authenticate_user(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    # Prepare to call the function
    #cursor.execute("SELECT id FROM Users WHERE name=:1", [username])
    result = cursor.callfunc("dfn_validate_login_user", str, [username, password])
    #result = cursor.fetchone()
    cursor.close()
    conn.close()
    #('output', result)
    if result == 'Y':
        return True
    else:
        return False
    #raise HTTPException(status_code=401, detail="Invalid username or password")

# authenticate_user('SYSTEM','support')

def user_menu_group(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("Select distinct groupnam,grpsrlno From vw_user_menu Where usercode = :1 order by grpsrlno", [username])    
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def user_menu(username: str, grupname: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("Select groupnam, progname, progtitl, grpsrlno, mensrlno From vw_user_menu Where usercode = :1 and groupnam = :2 order by grpsrlno, mensrlno", [username, grupname])    
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# grup = user_menu_group("AYMENB")
# for grp in grup:
#     menu_list = user_menu("AYMENB",grp[0])
#     for menu in menu_list:
#        print(grp[0], menu[1], menu[2])