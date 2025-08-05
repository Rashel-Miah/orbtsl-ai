import streamlit as st
#import requests
import json
from control.auth import authenticate_user, user_menu, user_menu_group
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
import uuid

st.set_page_config(page_title="Orbits AI", layout="centered")
#st.title("ChatBot 💬")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# keep the track if any new view is added to the database
if "new_view_added" not in st.session_state:
    st.session_state.new_view_added = None

# Initialize the llm model
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = "qwen2.5-coder:7b"

def apply_custom_css():  # Apply the custom css
    with open('static/style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def get_unique_thread_id():
    """Retrieves the unique session ID for the current Streamlit connection."""
    thread_id = uuid.uuid4()
    if thread_id:
        return thread_id
    return None

def login():
    st.markdown("<h1 style='text-align:center;'>Welcome to Orbits AI", unsafe_allow_html=True)    
    st.subheader("Log in")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login",type="primary",icon=":material/login:")
        #if st.button("Login", type="primary", icon=":material/login:"):
        if submitted:
            if username == "" or password == "":
                st.error("Enter the username and password")
            else:
            # res = requests.post("http://localhost:8000/login", data={"username":username, "password":password})
                res = authenticate_user(username, password)
                if res:
                # if res.status_code == 200:
                # if username == "admin" and password == "admin":
                    #print("Success")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.thread_id = get_unique_thread_id()
                    st.rerun()
                else:
                    st.error("Login failed")
                # st.rerun()

def logout():
   #requests.post("http://localhost:8000/logout", data={"username": st.session_state.username})
    st.session_state.logged_in = False
    st.session_state.username = None
    if 'messages' in st.session_state:
        st.session_state.messages = []
    st.rerun()

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
about_page = st.Page("about.py", title="About", icon=":material/help:",default=True)

revenue_page_1 = st.Page("inference/revenue_1.py", title="Taxi Revenue")
revenue_page_2 = st.Page("inference/revenue_2.py", title="Driver Revenue")
pickuploc_page = st.Page("graph/pickuploc_1.py", title="Pickup location map")
chatbot_page = st.Page("chat/chatbot.py", title="ChatBot")

inference_pages = [revenue_page_1,revenue_page_2]
graph_pages = [pickuploc_page]
chat_pages = [chatbot_page]

# st.title("Log In")
# st.logo("images/orbits_logo.png", icon_image="images/home_icon.png")
st.logo("images/orbits_logo.png", icon_image="images/orbits_logo.png")

page_dict = {}
# Generate the user rights wise menu list
if st.session_state.logged_in == True:
    grup = user_menu_group(st.session_state.username)
    for grp in grup:
        page_dict[grp[0]] = []
        menu_list = user_menu(st.session_state.username,grp[0])
        for menu in menu_list:
            #print(grp[0], menu[1], menu[2])
            page_dict[grp[0]].append(st.Page(menu[1], title=menu[2]))
#print(page_dict)    
# if st.session_state.username == 'SYSTEM':
#     page_dict["Inference"] = inference_pages
#     page_dict["Graph"] = graph_pages
#     page_dict["Chat"] = chat_pages
#     page_dict1 = {"inference":[st.Page('inference/revenue_1.py', title='Taxi Revenue'), st.Page('inference/revenue_2.py', title='Driver Revenue')],"graph":[st.Page('graph/pickuploc_1.py', title='Pickup Location Map')],"chat":[st.Page('chat/chatbot.py', title='ChatBot')]}    

if len(page_dict) > 0 and st.session_state.logged_in == True:
    pg = st.navigation({"Account": [logout_page,about_page]} | page_dict, position="sidebar")
else:
    pg = st.navigation([st.Page(login)])

apply_custom_css()

pg.run()