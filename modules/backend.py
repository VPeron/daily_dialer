import streamlit as st
import pandas as pd
from datetime import datetime


def get_current_date():
    """Get date string for sequential file name generation"""
    date_today = str(datetime.now())[:10]
    return date_today
    

@st.cache
def convert_df(df):
     """" IMPORTANT: Cache the conversion to prevent computation on every rerun"""
     return df.to_csv(index=False).encode('utf-8')


def clean_phone_number(num):
  '''
  strips special characters from phone numbers
  '''
  numbers = []
  for char in str(num):
    if char.isdigit():
      numbers.append(char)
  clean_number = ''.join(numbers)
  return clean_number


def process_outreach_one(df):
    """
    Receives 1st file as a dataframe, filters out cut-off dates 
    (cumulative from weekends on monday flow #TODO automate bank holidays) for first contact.
    
    """
    #TODO assert phone number is complete
    today_date = datetime.today()
    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    today = weekDays[today_date.weekday()]
    if today == 'Monday':
        df_day_filter = df[df['time_since_due_date'].str.contains(r"^7 d|^8 d|^9 d")]
    else:
        df_day_filter = df[df['time_since_due_date'].str.startswith('7 day')]
    
    df_day_filter.columns = ['account_code', 'first_name', 'last_name', 'email', 'number', 'tax_region', 'oldest_invoice', 'time_since_due_date',
                             'active_zendesk_created_date', 'setup_complete']
    df_day_filter = df_day_filter.copy()  # removes futurecopywithwarning (1st copy!)
    df_day_filter.drop(["setup_complete", "oldest_invoice", "account_code", "active_zendesk_created_date", "time_since_due_date"], axis=1, inplace=True)
    df_day_filter['uid'] = df_day_filter['email']
    df_day_filter['number'] = df_day_filter['number'].apply(clean_phone_number)
    cols = ['uid', 'number', 'first_name', 'last_name', 'email', 'tax_region']
    df_day_filter = df_day_filter[cols]
    
    df_day_filter = df_day_filter.drop_duplicates()
    
    sorted_regions = ['', 'HI', 'AK', 'WA', 'OR', 'NV', 'CA', 'MT', 'ID', 'WY', 'UT', 'CO', 'AZ', 
                      'NM', 'ND', 'SD', 'NE', 'KS', 'OK', 'TX', 'MN', 'IA', 'MO', 'AR', 'LA', 
                      'WI', 'IL', 'TN', 'MS', 'AL', 'MI', 'IN', 'KY', 'GA', 'FL', 'OH', 'WV', 
                      'ME', 'VT', 'NY', 'NH', 'MA', 'RI', 'CT', 'PA', 'NJ', 'DE', 'MD', 'DC', 'VA', 'NC', 'SC']
    region_dict = {}
    for index, region in enumerate(sorted_regions):
        region_dict[region] = index
    df_day_filter = df_day_filter.copy()  # removes futurecopywithwarning (2nd copy...)
    df_day_filter['region_index'] = df_day_filter['tax_region'].map(region_dict)
    df_day_filter.sort_values(by='region_index', axis=0, na_position='first', inplace=True)
    df_day_filter.drop('region_index', axis=1, inplace=True)
    df_day_filter = df_day_filter.drop_duplicates(subset=['number'])

    assert df_day_filter.number.nunique() == df_day_filter.email.nunique()
    
    return df_day_filter.reset_index(drop=True)


def process_outreach_two(df):
    """
    Remove payments before setting up for next contact.
    """
    df_or_1 = df
    # df_or_1.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 
    #                    'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_or_1 = df_or_1[["uid", "number", "status"]]
    df_or_1 = df_or_1[df_or_1.status != "sale"]  # also remove do not call?
    #df_or_1.head()
    
    
    return df_or_1


def process_pending_or1(df_pending):
    """
    optional file to be filtered and merged.
    """
    #df_pending.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 
                        #   'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_pending = df_pending[["uid", "number", "status"]]
    df_pending = df_pending[df_pending["status"] == 'new']
    

    return df_pending


def process_pending_or2(df_pending):
    """
    optional file to be filtered and merged.
    """
    # df_pending.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 
    #                       'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_pending = df_pending[["uid", "number", "status"]]
    df_pending = df_pending[df_pending['status'] == 'new']
    
    
    return df_pending


def multi_file(outreach):
    """
    handles all outreaches with the option to merge file data before downloading csv.
    """
    but_placeholder = st.empty()

    present_day = get_current_date()
    # FILE 1
    try:
        uploaded_file = st.file_uploader("Upload main file", key="main_file")
        if uploaded_file is not None:
            if outreach == 1:
                df = pd.read_csv(uploaded_file)
                df = process_outreach_one(df)
            if outreach == 2 or outreach == 3:
                df = pd.read_csv(uploaded_file, sep=';')
                df = process_outreach_two(df)
            st.write(uploaded_file.name)
            st.write(df)
            but_placeholder = st.empty()
            process = but_placeholder.button('Create File', key='done 1 file')
            if process:
                # DOWNLOAD
                csv = convert_df(df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{present_day}_outreach_{outreach}.csv',
                    mime='text/csv',
                )
    except KeyError:
            st.error('The file format does not match the requirements.')

    # FILE 2
    try:
        uploaded_file_2 = st.file_uploader("Upload pending outreach from yesterday", key='pendings')
        if uploaded_file_2 is not None and uploaded_file is not None:
            df_pending = pd.read_csv(uploaded_file_2, sep=";")
            if outreach == 1:
                df_pending = process_pending_or1(df_pending)
            if outreach == 2 or outreach == 3:
                df_pending = process_pending_or2(df_pending)

            st.write(uploaded_file_2.name)
            st.write(df_pending)
            
            confirm_merge = but_placeholder.button('Confirm merge', key='merge')
            if confirm_merge:
                df = df[['uid', 'number']]
                df['status'] = 'new'
                merged_df = df.append(df_pending)
                st.info(f'File Name: {present_day}_outreach_{outreach}.csv')
                
                # DOWNLOAD PROCESSED FILE 1 AND 2 MERGED
                csv = convert_df(merged_df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{present_day}_outreach_{outreach}.csv',
                    mime='text/csv',
                )
    except ValueError:
            st.error('The file format does not match the requirements.')
    
    # ONLY FILE 2 OPTION
    try:      
        if uploaded_file_2 is not None and uploaded_file is None:
            df_pending_only = pd.read_csv(uploaded_file_2, sep=";")
            if outreach == 1:
                df_pending_only = process_pending_or1(df_pending_only)
            if outreach == 2 or outreach == 3:
                df_pending_only = process_pending_or2(df_pending_only)
                
            st.write(uploaded_file_2.name)
            st.write(df_pending_only)
            # DOWNLOAD PROCESSED FILE 2 ONLY
            process = st.button('Create and download file', key='done only pending')
            if process:
                csv = convert_df(df_pending_only)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{present_day}_outreach_{outreach}.csv',
                    mime='text/csv',
                )
    except ValueError:
            st.error('The file format does not match the requirements.')


# FRAUD LISTS
def process_fraud_delinquents(df):
    """
    process MODE delinquents file
    """
    df.columns = ['account_code', 'first_name', 'last_name', 'email', 'phone', 'tax_region', 'oldest_invoice', 
                  'time_since_due_date', 'active_zendesk_created_date', 'setup_complete']
    today_date = datetime.today()
    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    today = weekDays[today_date.weekday()]
    if today == 'Monday':
        df_one_day = df[df['time_since_due_date'].str.contains(r"^1 d|^2 d|^3 d")]
    else:
        df_one_day = df[df['time_since_due_date'].str.contains('1 day ')]
    df_one_day = df_one_day['email'].drop_duplicates().reset_index().drop('index', axis=1)
    
    return df_one_day


def process_fraud_payments(df):
    """
    process MODE payments file
    """
    df['billed_date'] = pd.to_datetime(df['billed_date'])
    df['closed_at'] = pd.to_datetime(df['closed_at'])
    df["billed_date"] = df["billed_date"].dt.strftime('%Y-%m-%d')
    df["closed_at"] = df["closed_at"].dt.strftime('%Y-%m-%d %H:%M')
    df['email'] = df['email'].str.strip()
    df['email'] = df['email'].drop_duplicates()
    df.dropna(inplace=True)
    return df
    

def fraud_files(type):
    """
    file widgets, upload and download
    """
    st.image("https://mahoneysabol.com/wp-content/uploads/2020/08/Fraud_Blog-Header.jpg")
    
    present_day = get_current_date()
    
    ### DELINQUENTS ###
    if type == 'delinquents':
        st.info("""
                Upload dialer_daily_report directly from MODE.\n
    If today is Monday, weekend entries will be picked up automatically.""")
        # UPLOAD FILE
        uploaded_file = st.file_uploader("Upload dialer_daily_report file", key="fraud_delinquents")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            df = process_fraud_delinquents(df)
            st.write(f"{len(df.email)} lines to process.")
            st.write(df)
            csv = convert_df(df)
            # DOWNLOAD FILE
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'{present_day}_fraud_{type}.csv',
                mime='text/csv',
            )
            st.info(f'{present_day}_fraud_{type}.csv download is ready.')

    ### PAYMENTS ###
    if type == 'payments':
        st.warning("If you need to process multiple files at once, i.e: Mondays, merge the files manually before uploading.")
        
        uploaded_file = st.file_uploader("Upload dialer_daily_payments file", key="delinquent_payments")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            df = process_fraud_payments(df)
            st.write(f"{len(df.email)} lines to process.")
            st.write(df)
            csv = convert_df(df)
            # DOWNLOAD FILE
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'{present_day}_{type}.csv',
                mime='text/csv',
            )
            st.info(f'{present_day}_{type}.csv download is ready.')
        
        # notebook = st.checkbox('Colab Notebook')
        # if notebook:
        #     url = 'https://colab.research.google.com/drive/1GNnG8_KUXQB8wtmGzYYn9KbOzvY8Fy6V#scrollTo=1WFm-0AiolkU'
        #     st.markdown(f'<a href="{url}">You can also use Colab notebook for payments, if you have access to it.', unsafe_allow_html=True)
            
        #     st.info("""
        #             See contact page if you need access to the notebook and prefer it.
        #             """)
