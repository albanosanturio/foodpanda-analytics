import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Emojis to select from 🔴🟣🐼

# Load data
df = pd.read_csv('data/foodpanda_raw.csv')
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Order_Month'] = df['Order_Month'].str.replace('-2024', '') #redundant, all info is from such year

# Define month order (chronological)
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
df['Order_Month'] = pd.Categorical(df['Order_Month'], categories=month_order, ordered=True)


# Columns that we could delete:
# Customer_Name - not used, and too much information, based on who accesses this dashboard may be necessary to delete
# Customer_Phone - same logic
# Customer_ID - same logic
# Delivery_Address - same logic
# Restaurant_Address - not used, we be using lat and long to infer distance
# Product_Name - not used, we aggregate at restaurant or type of food level
# Rider_Name - not used and also could be too much info
# Rider_ID - same logic


# Page config
st.set_page_config(page_title="FoodPanda Analytics", layout="wide")
st.title("FoodPanda Analytics Dashboard")

# Add background image from local file
with open('pattern30.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('data:image/png;base64,{image_data}');
        background-attachment: fixed;
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR FILTERS
st.sidebar.header("Filters")

# Country filter with "All" option
countries = sorted(df['Delivery_Country'].unique())
country = st.sidebar.selectbox('Country', ['All'] + list(countries))

if country == 'All':
    df_filtered = df.copy()
else:
    df_filtered = df[df['Delivery_Country'] == country]

# City filter with "All" option
cities = sorted(df_filtered['Delivery_City'].unique())
city = st.sidebar.selectbox('City', ['All'] + list(cities))

if city == 'All':
    pass  # Keep all cities
else:
    df_filtered = df_filtered[df_filtered['Delivery_City'] == city]





# # Month filter with "All" option
# months = sorted(df_filtered['Order_Month'].unique())
# month = st.sidebar.selectbox('Month', ['All'] + list(months))
# 
# if month != 'All':
#     df_filtered = df_filtered[df_filtered['Order_Month'] == month]

# Month filter with multiselect (clickable boxes)
# months = sorted(df_filtered['Order_Month'].unique())
# selected_months = st.sidebar.multiselect('Month', months, default=months)
# 
# if selected_months:
#     df_filtered = df_filtered[df_filtered['Order_Month'].isin(selected_months)]

# Month filter with clickable toggle buttons
months_filtered = df_filtered['Order_Month'].unique()

# Sort by the categorical order (not alphabetically)
months = sorted(months_filtered, key=lambda x: month_order.index(str(x)))

# Initialize session state
if 'selected_months' not in st.session_state:
    st.session_state.selected_months = set(months)

st.sidebar.markdown("**Month**")

# "All Months" button - purple with more emphasis
col1, col2, col3 = st.sidebar.columns([0.5, 1, 0.5])
with col2:
    if st.button("**𝐀𝐋𝐋 𝐌𝐎𝐍𝐓𝐇𝐒**", key="all_months_btn", use_container_width=True):
        st.session_state.selected_months = set(months)
        st.rerun()

# Month buttons with visual feedback
cols = st.sidebar.columns(4)

for idx, month in enumerate(months):
    col = cols[idx % 4]
    is_selected = month in st.session_state.selected_months
    # Green dot if selected, grey dot if not
    if is_selected:
        display_text = f"🔴 {month}"
    else:
        display_text = f"⚪ {month}"
    
    if col.button(display_text, key=f"month_{month}", use_container_width=True):
        if is_selected:
            st.session_state.selected_months.discard(month)
        else:
            st.session_state.selected_months.add(month)
        st.rerun()

# Filter data by selected months
if st.session_state.selected_months:
    df_filtered = df_filtered[df_filtered['Order_Month'].isin(st.session_state.selected_months)]



# MAIN DASHBOARD
st.header("Orders by Restaurant Category")
category_orders = df_filtered.groupby('Restaurant_Category').size().reset_index(name='count')
fig = px.bar(category_orders, x='Restaurant_Category', y='count', title='Volume of Orders by Category')



# Customize hover to show ONLY the count number
fig.update_traces(hovertemplate='%{y}<extra></extra>')
st.plotly_chart(fig, use_container_width=True)