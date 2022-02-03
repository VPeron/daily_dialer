import streamlit as st
from datetime import datetime
from modules.backend import multi_file, fraud_delinquents, fraud_payments

FRONT_PASSWORD = st.secrets["front_password"]
EMAIL_CONTACT = st.secrets['email_contact']


st.set_page_config(page_title='Daily Dialer', page_icon="☎️", layout='centered')

hide_streamlit_style = """
    <style>
    #MainMenu {visibility:hidden;}
    footer {
        visibility:hidden;
    }
    footer:after {
        content: 'Made For Canary ®️';
        visibility: visible;
        display: block;
        position: relative;
        #background-color: red;
        padding: 5px;
        top: 2px;
    }
    .st-at {
    background-color: ##0E1117;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

today_date = str(datetime.today())[:10]


def front_door():
    session_state = False
    main_col_1, main_col_2, main_col_3 = st.columns([1,4,1])
    with main_col_1:
        st.write('')
    
    with main_col_2:
        front_placeholder = st.empty()
        img_placeholder = st.empty()
        front_placeholder.title(' ☘ « ※ » ♠🅲♠ « ※ » ☘')
        ## AUTHENTICATION ##
        placeholder = st.empty()
        img_placeholder.image('https://cdn.dribbble.com/users/56941/screenshots/1078625/canary_logo_3.png')
        input_password = placeholder.text_input(' 🔑 :', value='', type='password')
        if input_password:
            if input_password == FRONT_PASSWORD:
                session_state = True
                    
                front_placeholder.empty()
                placeholder.empty()
                img_placeholder.empty()
            else:
                placeholder.image('https://www.how-to-draw-funny-cartoons.com/image-files/cartoon-chair-6.gif')
                session_state = False
                st.stop()
        
    with main_col_3:
        st.write('')
    return session_state


def home_page():
    st.image('https://smarthomesolver.com/reviews/wp-content/uploads/2016/09/canary_transparent_logo-e1478312785944.png')
    st.title('« ※ » Dialer Files « ※ »')
    st.info("""Select an Outreach or a Fraud list type from the sidebar menu.\n
See About and Contact pages if you need any help.""")


def multi_file_page():
    st.title("Dunning Outreaches")
    outreach_option = st.selectbox('Select your outreach: ', [None, 1, 2, 3])
    if outreach_option is not None:
        multi_file(outreach_option)
    

def fraud_delinquents_page():
    fraud_delinquents()
    st.title('FRAUD DELINQUENTS')
    st.warning('Coming soon')


def fraud_payments_page():
    fraud_payments()
    st.title('FRAUD PAYMENTS')
    st.warning('Coming soon')
    

def contact_page():
    st.title('Contact: 📧')
    table_info = {
        'Email': [EMAIL_CONTACT],
        'Github/Source Code': ["https://github.com/VPeron/daily_dialer"],
        
    }
    st.table(table_info)
    
    
def about_page():
    st.title('About')
    st.info("""Simple UI app to aid file formatting routine.\n
Outreaches 1, 2 and 3 are available via sidebar menu.
- Outreach 1 expects a .csv file from MODE where it will filter the respective data to be used for the current date. This file will be ready to go into Babelforce as Outreach 1.
- Outreaches 2 and 3 expect a file with .csv extension (but with semicolon delimiter) from BabelForce containing a status column with the outcome of outreaches 1 and 2, respectively.\n
- For all outreaches, a file will be created in your Downloads directory and should be ready to be uploaded into Babelforce.\n
A contact page is available for any help or suggestions.\n
Version 1.0\n
01/02/2022\n
""")
        

def main():
    # Register pages
    pages = {
        "Homepage": home_page,
        "Dunning outreaches": multi_file_page,
        "Blocklist": fraud_delinquents_page,
        "Late Payments": fraud_payments_page,
        "About": about_page,
        "Contact": contact_page,
    }
    
    page = st.sidebar.radio("Menu", tuple(pages.keys()))
    pages[page]()
    
    
if __name__ == "__main__":
    base_auth = front_door()
    if base_auth:
        main()
