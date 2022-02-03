import streamlit as st
import pandas as pd
from datetime import datetime


PRESENT_DAY = str(datetime.today())[:10]

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
    Receives 1st file as a dataframe, filters out cut-off dates (cumulative from weekends on monday flow #TODO automate bank holidays) for first contact.
    
    """
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
    df_day_filter = df_day_filter.copy()  # removes futurecopywithwarning (2nd copy!)
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
    df_or_1.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    # df_or_1.drop(0, axis=0, inplace=True)
    df_or_1 = df_or_1[df_or_1.status != "sale"]  # also remove do not call?
    df_or_1.head()
    
    df_or_1 = df_or_1[["uid", "number", "status"]]
    
    return df_or_1

def process_pending_or1(df_pending):
    df_pending.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_pending = df_pending[df_pending["status"] == 'pending']
    df_pending = df_pending[["uid", "number", "status"]] # status == pending

    return df_pending


def process_pending_or2(df_pending):
    df_pending.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_pending = df_pending[df_pending['status'] == 'pending']
    df_pending = df_pending[["uid", "number", "status"]]
    return df_pending



def multi_file(outreach):
    """
    handles all outreaches with the option to merge file data before downloading csv.
    """
    but_placeholder = st.empty()

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
                csv = convert_df(df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{PRESENT_DAY}_outreach_{outreach}.csv',
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

                st.info(f'File Name: {PRESENT_DAY}_outreach_{outreach}.csv')
                # st.write(merged_df) # expecting bytes obj? can't display table here
                # DOWNLOAD PROCESSED FILE 1 AND 2 MERGED
                csv = convert_df(merged_df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{PRESENT_DAY}_outreach_{outreach}.csv',
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
                    file_name=f'{PRESENT_DAY}_outreach_{outreach}.csv',
                    mime='text/csv',
                )
    except ValueError:
            st.error('The file format does not match the requirements.')


def fraud_delinquents():
    pass



def fraud_payments():
    pass


