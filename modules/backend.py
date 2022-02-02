import streamlit as st
from datetime import datetime


@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
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
    df_or_1 = df
    df_or_1.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 
                       'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    df_or_1.drop(0, axis=0, inplace=True)
    df_or_1 = df_or_1[df_or_1.status != "sale"]  # remove rows with sale status  -> remove do not call?
    df_or_1.head()

    #TODO multiple file flow
    # if len(file_2) > 0:
    #     worksheet_2 = gc.open(str(file_2)).sheet1
    #     data_2 = worksheet_2.get_all_values()
    # file_2_list = []
    # for item in data_2:
    #     for current_row_2 in item:
    #         file_2_list.append(current_row_2.split(';'))
    # df_or_2 = pd.DataFrame(file_2_list)
    # df_or_2.columns = ['id', 'campaignId', 'listId', 'uid', 'number', 'status', 'dateCreated', 'lastUpdated', 'dateCalled', 'callCount', 'duration', 'calledSinceReset', 'rank', 'data', '_url']
    # df_or_2.drop(0, axis=0, inplace=True)
    # df_or_2 = df_or_2[df_or_2.status == "pending"]  # keep only rows with pending
    # df_or_1.append(df_or_2)
    
    df_or_1 = df_or_1[["uid", "number", "status"]]
    
    return df_or_1
