import streamlit as st
from datetime import datetime
import pandas as pd

from modules.backend import process_outreach_one, process_outreach_two, convert_df


FRONT_PASSWORD = st.secrets["dialer_password"]

st.set_page_config(page_title='Daily Dialer', page_icon="🔒", layout='centered')

hide_streamlit_style = """
    <style>
    #MainMenu {visibility:hidden;}
    footer {
        visibility:hidden;
    }
    footer:after {
        content: 'Made For Canary';
        visibility: visible;
        display: block;
        position: relative;
        #background-color: red;
        padding: 5px;
        top: 2px;
    }
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
        front_placeholder.title(' ☘ « ※ » ♠🔒♠ « ※ » ☘')
        ## AUTHENTICATION ##
        placeholder = st.empty() 
        input_password = placeholder.text_input(' 🔑 :', value='', type='password')
        if input_password:
            if input_password == FRONT_PASSWORD:
                session_state = True
                    
                front_placeholder.empty()
                placeholder.empty()
            else:
                placeholder.image('https://www.how-to-draw-funny-cartoons.com/image-files/cartoon-chair-6.gif')
                session_state = False
                st.stop()
        
    with main_col_3:
        st.write('')
    return session_state


def home_page():
    st.title('« ※ » ☘ Canary - Dialer files ☘ « ※ » ')
    st.image("https://marketbusinessnews.com/wp-content/uploads/2020/06/Auto-dialers-image-for-article-a-button-phone.jpg")
    st.info("See contact page if you need any help.")
    

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
            confirm_process = st.button('Process file', key='confirm_processing_1')
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
        outreach_option = st.selectbox('Chose outreach: ', [None, '2', '3'])
        if outreach_option is not None:
            uploaded_file = st.file_uploader("Choose a CSV file", key="OR23")
        
            if uploaded_file is not None:
                raw_data = pd.read_csv(uploaded_file)
                temp_data = process_outreach_two(raw_data)
                # 2 - VIZ NEW DF
                st.write(temp_data)

                # 3 - CONFIRM
                confirm_process = st.button('Process file', key='confirm_processing_2')
                if confirm_process:
                    # 4 - DOWNLOAD PROCESSED FILE
                    csv = convert_df(temp_data)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name=f'{today_date}_outreach_{outreach_option}.csv',
                        mime='text/csv',
                    )
    

def contact_page():
    st.title('Contact')
    st.write('Email: vinicius.peron@canary.is')
    st.warning('Further info coming soon.')
        

def main():
    # Register your pages
    pages = {
        "Homepage": home_page,
        "Outreach 1": outreach_one,
        "Outreaches 2/3": outreach_two_and_three,
        "Contact": contact_page,
    }
    
    page = st.sidebar.selectbox("Select your outreach", tuple(pages.keys()))
    pages[page]()
    
    
if __name__ == "__main__":
    base_auth = front_door()
    if base_auth:
        main()