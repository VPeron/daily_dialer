import streamlit as st
from datetime import datetime
import pandas as pd

from modules.backend import process_outreach_one, process_outreach_two, convert_df


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
    st.info("""Select the outreach from the sidebar menu.\n
See About and Contact pages if you need any help.""")
    

def outreach_one():
    with st.container():
        st.title('OUTREACH 1')
        
        # 1 - DROP CSV
        uploaded_file = st.file_uploader("Choose a CSV file", key="OR1")
        if uploaded_file is not None:
            raw_data = pd.read_csv(uploaded_file)
            temp_data = process_outreach_one(raw_data)
            # 2 - VIZ NEW DF
            st.write(temp_data)
            # 3 - CONFIRM
            confirm_process = st.button('Create file', key='confirm_processing_1')
            if confirm_process:
                # 4 - DOWNLOAD PROCESSED FILE
                csv = convert_df(temp_data)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{today_date}_outreach_1.csv',
                    mime='text/csv',
                )
    

def outreach_two_and_three():
    with st.container():
        st.title('OUTREACHES 2 & 3')
        st.warning("""This outreach expects files coming out of Babelforce.\n
Please ensure you first open the file in a notepad and replace all ';' with a coma ','
""")
        
        # 1- Select outreach (output file naming purposes only)
        outreach_option = st.selectbox('Chose outreach: ', [None, '2', '3'])
        if outreach_option is not None:
            # 2 - DROP CSV
            uploaded_file = st.file_uploader("Choose a CSV file", type='csv', key="OR23")
            if uploaded_file is not None:
                raw_data = pd.read_csv(uploaded_file)
                
                # st.write(raw_data)
                
                temp_data = process_outreach_two(raw_data)
                # 3 - VIZ NEW DF
                st.write(temp_data)
                # 4 - CONFIRM
                confirm_process = st.button('Create file', key='confirm_processing_2')
                if confirm_process:
                    # 5 - DOWNLOAD PROCESSED FILE
                    csv = convert_df(temp_data)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name=f'{today_date}_outreach_{outreach_option}.csv',
                        mime='text/csv',
                    )
    

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
- Outreach 1 expects a .csv file from MODE where it will filter the respective data for the present day.
- Outreaches 2 and 3 expect a .csv file from BabelForce containing a status column with the outcome of outreaches 1 and 2, respectively.\n
A contact page is available for any help or suggestions.\n
Version 1.0\n
01/02/2022\n
""")
        

def main():
    # Register pages
    pages = {
        "Homepage": home_page,
        "Outreach 1": outreach_one,
        "Outreaches 2/3": outreach_two_and_three,
        "About": about_page,
        "Contact": contact_page,
        
    }
    
    page = st.sidebar.radio("Menu", tuple(pages.keys()))
    pages[page]()
    
    
if __name__ == "__main__":
    base_auth = front_door()
    if base_auth:
        main()
