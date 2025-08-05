import oracledb
import streamlit as st 
#from langchain_community.utilities import SQLDatabase

DB_CONFIG = {
    "user": st.secrets.db_credentials.user,
    #"user": 'aitest',
    "password": st.secrets.db_credentials.password,
    #"password": "aitest",
    "dsn": st.secrets.db_credentials.dsn,
    #"dsn": "localhost:1521/orcl.amernitech.com",
    "min": 2,
    "max": 5,
    "increment": 1    
}
#connection_uri = f"oracle+cx_oracle://{st.secrets.db_credentials.user}:{st.secrets.db_credentials.password}@{st.secrets.db_credentials.hostport}?service_name={st.secrets.db_credentials.srvcname}"
#db = SQLDatabase.from_uri(connection_uri, include_tables=True,include_views=True,view_support=True)
#print(st.secrets.db_credentials.srvcname)

_pool = None

def init_pool():
    global _pool
    if not _pool:
        _pool = oracledb.create_pool(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=DB_CONFIG["dsn"],
            min=DB_CONFIG["min"],
            max=DB_CONFIG["max"],
            increment=DB_CONFIG["increment"],
            getmode=oracledb.SPOOL_ATTRVAL_WAIT,
            timeout=10
        )
    return _pool

def execute_query(sql: str) -> str:
    try:
        # pool = await init_pool()
        pool = init_pool()
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description:
                    rows = cursor.fetchall()
                    #print("Rows: ",rows)
                    #columns = [col[0] for col in cursor.description]
                    #return [dict(zip(columns, row)) for row in rows]
                    return rows
                else:
                    return {"status": "Query executed successfully."}
    except Exception as e:
        return {"error": str(e)}

#result = execute_query("SELECT SUM(taxi_revenue) FROM vw_taxi_collection")  
#print(result)
#print("Successfully connected to Oracle Database")


#def schemas():
#    result = execute_query("select count(*) from users")
#    print(result)

#schemas()