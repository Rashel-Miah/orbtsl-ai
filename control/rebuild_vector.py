from chat.utils.examples import add_example
from chat.utils.example_store import build_or_load_example_selector
from control.db import get_connection
import datetime
import streamlit as st 
from chat.utils.schema_store import build_or_load_schema_store
from shutil import rmtree

st.set_page_config(page_title="Control", layout="centered")
st.title("Rebuild :blue[Vector DB]")

def check_new_example_added():
    conn = get_connection()
    cursor = conn.cursor()
    result = cursor.callfunc("dfn_new_examlpe_add_flag", str)
    cursor.close()
    conn.close()
    #print(result)
    return result

def read_new_examples():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("Select example_id, user_input, sql_query From add_examples Where new_flag = 'Y'")
    #rows = [{"example_id": row[0], "input": row[1], "query": row[2]} for row in cursor]
    rows = cursor.fetchall()
    #print(rows)
    conn.close()
    return rows

def add_new_examples() -> bool:
    new_examples = read_new_examples()
    #example_id_track: int
    for row in new_examples:
        #example_id_track = row[0]
        add_example(row[1],row[2])
    return True

curr_id : int

# Update to the DB after adding to the json file and rebuild the vector DB.
def update_new_example_flag() -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE add_examples SET new_flag='N', LOAD_TIME=sysdate WHERE new_flag='Y'")
    conn.commit()
    conn.close()
    return True        

# Rebuild the vector DB after updating to the json file
def rebuild_example_vector_store() -> bool:
    # Clear the cache
    build_or_load_example_selector.clear()
    # Rebuild forcely
    build_or_load_example_selector(force_rebuild=True)
    return True

def check_new_schema_added():
    conn = get_connection()
    cursor = conn.cursor()
    result = cursor.callfunc("dfn_new_view_add_flag", str)
    cursor.close()
    conn.close()
    #print(result)
    return result

def rebuilt_scema_vector_store() -> bool:
    build_or_load_schema_store.clear()
    build_or_load_schema_store(force_rebuild=True)
    return True

def update_new_schema_load_flag():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE NEW_VIEW_ADD SET NEW_FLAG = 'N' WHERE NEW_FLAG = 'Y'")
    conn.commit()
    conn.close()
    return {"message": "updated successfully"}   

new_schema_flag = check_new_schema_added()
new_example_flag = check_new_example_added()

with st.form('control'):
    new_example = st.checkbox("New example added flag.")
    new_schema = st.checkbox("New schema added flag.")

    submitted = st.form_submit_button("Update",type='primary')

if submitted:
    with st.spinner("Re-building the vector DB.........."):
        if new_example and new_example_flag == 'Y':
            # Add to the json file
            added_example = add_new_examples() 
            if added_example:
                rebuild_example_vector = rebuild_example_vector_store()

            if rebuild_example_vector:
                #curr_date:str = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                #print(curr_date)
                # Update the new example flag to 'N' after adding to the json file and rebuild the vector store
                #updated_new_example = update_new_example_flag(curr_id,curr_date)
                updated_new_example = update_new_example_flag()
        
        if new_schema and new_schema_flag == 'Y':
            rebuilt_scema_vector = rebuilt_scema_vector_store()
            if rebuilt_scema_vector:
                update_new_schema_load_flag()

        st.write("Updated Successfully")