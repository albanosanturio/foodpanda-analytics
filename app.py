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
        display_text = f"🟣 {month}"
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

# KPI CARDS with larger font
st.markdown("---")
st.header("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = len(df_filtered)
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    gmv = df_filtered['Gross_Revenue_USD'].sum()
    st.metric("GMV", f"${gmv:,.0f}")

with col3:
    gross_profit = df_filtered['Gross_Profit_USD'].sum()
    st.metric("Gross Profit", f"${gross_profit:,.0f}")

with col4:
    margin = df_filtered['Profit_Margin_Pct'].mean()
    st.metric("Margin %", f"{margin:.1f}%")
st.markdown("---")


# FINANCIALS SECTION
st.header("Financials") 

# Profit Trends by Month (Stacked by Category)

# Calculate profit by month and category
profit_by_month = df_filtered.groupby(['Order_Month', 'Restaurant_Category'])['Gross_Profit_USD'].sum().reset_index()

# Create stacked bar chart
fig_month = px.bar(profit_by_month, 
                   x='Order_Month', 
                   y='Gross_Profit_USD',
                   color='Restaurant_Category',
                   title='Total Gross Profit by Month (Stacked by Category)',
                   labels={'Gross Profit USD': 'Gross Profit ($)'},
                   barmode='stack')

fig_month.update_traces(hovertemplate='%{y:$.2f}<extra></extra>')
st.plotly_chart(fig_month, use_container_width=True)

# Calculate profit metrics by category
profitability = df_filtered.groupby('Restaurant_Category').agg({
    'Gross_Profit_USD': ['sum', 'mean', 'count']
}).reset_index()

profitability.columns = ['Restaurant_Category', 'Total_Profit', 'Profit_Per_Order', 'Order_Count']
profitability = profitability.sort_values('Total_Profit', ascending=False)

# Total Profit per Category (smaller, centered numbers)
st.markdown("<p style='font-size: 12px; color: #666; margin: 5px 0;'><b>Total Profit</b></p>", unsafe_allow_html=True)
cols = st.columns(len(profitability))

for idx, (col, row) in enumerate(zip(cols, profitability.itertuples())):
    with col:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 12px; margin: 0; color: #666;">{row.Restaurant_Category}</p>
            <p style="font-size: 20px; font-weight: bold; margin: 0; color: #7B2CBF;">${row.Total_Profit:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)


# Average Profit Per Order (smaller, centered numbers)
st.markdown("<p style='font-size: 12px; color: #666; margin: 5px 0;'><b>Average</b></p>", unsafe_allow_html=True)
cols = st.columns(len(profitability))

for idx, (col, row) in enumerate(zip(cols, profitability.itertuples())):
    with col:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 12px; margin: 0; color: #666;">{row.Restaurant_Category}</p>
            <p style="font-size: 20px; font-weight: bold; margin: 0; color: #7B2CBF;">${row.Profit_Per_Order:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

# COST ANALYSIS timeline + breakdown
st.markdown("---")
st.header("Cost analysis")


# Total Cost Trend by Month (Line Chart)
st.subheader("Total Cost Trend by Month")

# Calculate total cost by month
cost_by_month = df_filtered.groupby('Order_Month')['Total_Cost_USD'].sum().reset_index()

# Create line chart
fig_cost_trend = px.line(cost_by_month, x='Order_Month', y='Total_Cost_USD',
                         title='Total Cost by Month',
                         labels={'Total_Cost_USD': 'Total Cost ($)'})

# Style: minimal, purple line
fig_cost_trend.update_traces(
    line=dict(color='#7B2CBF', width=3),
    hovertemplate='%{y:$.0f}<extra></extra>'
)

fig_cost_trend.update_layout(
    hovermode='x unified',
    showlegend=False,
    xaxis_title='',
    yaxis_title='',
    height=300,
    yaxis=dict(showgrid=False),
    xaxis=dict(side='top')
)

st.plotly_chart(fig_cost_trend, use_container_width=True)


# Calculate total costs by type
cost_breakdown = pd.DataFrame({
    'Cost Type': ['Food Cost', 'Rider Salary', 'Marketing', 'Packaging'],
    'Amount': [
        df_filtered['Food_Cost_USD'].sum(),
        df_filtered['Rider_Salary_Cost_USD'].sum(),
        df_filtered['Marketing_Cost_USD'].sum(),
        df_filtered['Packaging_Cost_USD'].sum()
    ]
})

# Create pie chart with legend at bottom
fig_cost = px.pie(cost_breakdown, values='Amount', names='Cost Type',
                  title='Cost Breakdown by Category')

fig_cost.update_traces(hovertemplate='%{label}: $%{value:,.0f}<extra></extra>')
fig_cost.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))

# Layout: Pie chart on left, data on right
col_chart, col_data = st.columns([1, 1])

with col_chart:
    st.plotly_chart(fig_cost, use_container_width=True)

with col_data:
    # Add spacing to align with pie chart (increased)
    st.markdown("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
    
    # Headers with proper alignment (matching value row structure)
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="flex: 1;"></div>
        <p style="font-size: 12px; font-weight: bold; margin: 0; color: #666; flex: 1; text-align: center;">Total</p>
        <p style="font-size: 12px; font-weight: bold; margin: 0; color: #666; flex: 1; text-align: center;">Average/order</p>
    </div>
    """, unsafe_allow_html=True)

    # Data rows
    cost_types = ['Food_Cost_USD', 'Rider_Salary_Cost_USD', 'Marketing_Cost_USD', 'Packaging_Cost_USD']
    cost_labels = ['Food Cost', 'Rider Salary', 'Marketing', 'Packaging']

    for label, col_name in zip(cost_labels, cost_types):
        total = df_filtered[col_name].sum()
        avg = df_filtered[col_name].mean()

        st.markdown(f"""
        <div style="margin-bottom: 20px; display: flex; align-items: center;">
            <p style="font-size: 12px; margin: 0; color: #D3D3D3; flex: 1;">{label}</p>
            <p style="font-size: 16px; font-weight: bold; margin: 0; color: #7B2CBF; flex: 1; text-align: center;">${total:,.0f}</p>
            <p style="font-size: 16px; font-weight: bold; margin: 0; color: #7B2CBF; flex: 1; text-align: center;">${avg:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

