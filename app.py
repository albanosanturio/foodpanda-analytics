import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from geopy.distance import geodesic

# Emojis to select from 🔴🟣🐼

# Load data
df = pd.read_csv('data/foodpanda_raw.csv')
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Order_Month'] = df['Order_Month'].str.replace('-2024', '') #redundant, all info is from such year

# Define month order (chronological)
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
df['Order_Month'] = pd.Categorical(df['Order_Month'], categories=month_order, ordered=True)


# Adding distance column (infering from latitude and longitude data)
df['Delivery_Distance_km'] = df.apply(
    lambda row: geodesic(
        (row['Restaurant_Latitude'], row['Restaurant_Longitude']),
        (row['Delivery_Latitude'], row['Delivery_Longitude'])
    ).km, axis=1
)

# Columns that we could delete:
# Customer_Name - not used, and too much information, based on who accesses this dashboard may be necessary to delete
# Customer_Phone - same logic
# Customer_ID - same logic
# Delivery_Address - same logic
# Restaurant_Address - not used, we be using lat and long to infer distance
# Product_Name - not used, we aggregate at restaurant or type of food level
# Rider_Name - not used and also could be too much info
# Rider_ID - same logic


# Page config - TITLE
st.set_page_config(page_title="FoodPanda Analytics", layout="wide")


# Add background image to sidebar only
# Load both pattern images
with open('pattern-light.png', 'rb') as f:
    light_image_data = base64.b64encode(f.read()).decode()

with open('pattern-darkest.png', 'rb') as f:
    dark_image_data = base64.b64encode(f.read()).decode()

## st.markdown(f"""
##     <style>
##     @media (prefers-color-scheme: light) {{
##         [data-testid="stSidebar"] {{
##             background-image: url('data:image/png;base64,{light_image_data}');
##             background-attachment: fixed;
##             background-size: 40%;
##             opacity: 1;
##         }}
##     }}
##     
##     @media (prefers-color-scheme: dark) {{
##         [data-testid="stSidebar"] {{
##             background-image: url('data:image/png;base64,{dark_image_data}');
##             background-color: rgba(255,255,255,0.3);
##             background-blend-mode: multiply;
##             background-attachment: fixed;
##             background-size: 40%;
##             opacity: 1;
##         }}
##     }}
##     </style>
##     """, unsafe_allow_html=True)

## st.markdown(f"""
##     <style>
##     .stApp {{
##         background-attachment: fixed;
##         background-size: cover;
##         opacity: 0.9;
##     }}
##     </style>
##     """, unsafe_allow_html=True)


st.title("🐼 FoodPanda Analytics Dashboard 🐼")


# BUILDING SIDEBAR FILTERS
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


st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)


# START BUILDING DASHBOARD CONTENT AND METRICS #7B2CBF

# KPI CARDS with larger font

col1, col2, col3, col4 = st.columns(4)
total_orders = len(df_filtered)
gmv = df_filtered['Gross_Revenue_USD'].sum()
gross_profit = df_filtered['Gross_Profit_USD'].sum()
margin = df_filtered['Profit_Margin_Pct'].mean()

with col1:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border: 2px solid #7B2CBF ; border-radius: 8px;">
        <p style="font-size: 12px; text-align: center; margin: 0 0 10px 0;">Total Orders</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0;">{total_orders:,}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border: 2px solid #7B2CBF; border-radius: 8px;">
        <p style="font-size: 12px; text-align: center; margin: 0 0 10px 0;">GMV</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0;">${gmv:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border: 2px solid #7B2CBF; border-radius: 8px;">
        <p style="font-size: 12px; text-align: center; margin: 0 0 10px 0;">Gross Profit</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0;">${gross_profit:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border: 2px solid #7B2CBF; border-radius: 8px;">
        <p style="font-size: 12px; text-align: center; margin: 0 0 10px 0;">Margin %</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0;">{margin:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)


# FINANCIALS SECTION
st.markdown("---")
st.header("01. Financials") 

# Profit Trends by Month (Stacked by Category)

# Calculate profit by month and category
profit_by_month = df_filtered.groupby(['Order_Month', 'Restaurant_Category'])['Gross_Profit_USD'].sum().reset_index()

# Create stacked bar chart
fig_month = px.bar(profit_by_month, 
                   x='Order_Month', 
                   y='Gross_Profit_USD',
                   color='Restaurant_Category',
                   title='financials - profit - Total Gross Profit by Month (Stacked by Category)',
                   labels={'Gross Profit USD': 'Gross Profit ($)'},
                   color_discrete_map={
                       'Cafe': '#FF1493',
                       'Casual Dining': '#6C63FF',
                       'Fast Food': '#FF006E',
                       'Fine Dining': '#7B2CBF'
                   },
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
st.markdown("<p style='font-size: 12px;  margin: 5px 0;'><b>Total Profit</b></p>", unsafe_allow_html=True)
cols = st.columns(len(profitability))

for idx, (col, row) in enumerate(zip(cols, profitability.itertuples())):
    with col:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 12px; margin: 0; ">{row.Restaurant_Category}</p>
            <p style="font-size: 20px; font-weight: bold; margin: 0; color: #7B2CBF;">${row.Total_Profit:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)


# Average Profit Per Order (smaller, centered numbers)
st.markdown("<p style='font-size: 12px;  margin: 5px 0;'><b>Average</b></p>", unsafe_allow_html=True)
cols = st.columns(len(profitability))

for idx, (col, row) in enumerate(zip(cols, profitability.itertuples())):
    with col:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 12px; margin: 0; ">{row.Restaurant_Category}</p>
            <p style="font-size: 20px; font-weight: bold; margin: 0; color: #7B2CBF;">${row.Profit_Per_Order:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

# COST ANALYSIS timeline + breakdown


# Total Cost Trend by Month (Line Chart)

# Calculate total cost by month
cost_by_month = df_filtered.groupby('Order_Month')['Total_Cost_USD'].sum().reset_index()

# Create line chart
fig_cost_trend = px.line(cost_by_month, x='Order_Month', y='Total_Cost_USD',
                         title='financials - cost - Total Cost by Month',
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
fig_cost = px.pie(cost_breakdown, 
                  values='Amount', 
                  names='Cost Type',
                  title='financials - cost - Cost Breakdown by Category',
                  color_discrete_sequence=['#FF1493', '#6C63FF', '#FF006E', '#7B2CBF'])

fig_cost.update_traces(hovertemplate='%{label}: $%{value:,.0f}<extra></extra>')
fig_cost.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))

# Layout: Pie chart on left, data on right
col_chart, col_data = st.columns([1, 0.6])

with col_chart:
    st.plotly_chart(fig_cost, use_container_width=True)

with col_data:
    # Add spacing to align with pie chart (increased)
    st.markdown("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
    
    # Headers with proper alignment (matching value row structure)
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="flex: 1;"></div>
        <p style="font-size: 12px; font-weight: bold; margin: 0; flex: 1; text-align: center;">Total</p>
        <p style="font-size: 12px; font-weight: bold; margin: 0; flex: 1; text-align: center;">Average/order</p>
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
            <p style="font-size: 12px; margin: 0; flex: 1;">{label}</p>
            <p style="font-size: 16px; font-weight: bold; margin: 0; color: #7B2CBF; flex: 1; text-align: center;">${total:,.0f}</p>
            <p style="font-size: 16px; font-weight: bold; margin: 0; color: #7B2CBF; flex: 1; text-align: center;">${avg:.2f}</p>
        </div>
        """, unsafe_allow_html=True)



# CUSTOMER BEHAVIOUR SECTION
st.markdown("---")
st.header("02. Customer behaviour")

# ORDER VALUE DISTRIBUTION (HISTOGRAM - FIXED BUCKETS)

# Create fixed buckets (10, 20, 30... 100+)
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
labels = ['$0-10', '$10-20', '$20-30', '$30-40', '$40-50', '$50-60', '$60-70', '$70-80', '$80-90', '$90-100', '$100+']

df_filtered['Value_Bucket'] = pd.cut(df_filtered['Net_Order_Value_USD'], bins=bins, labels=labels)
value_dist = df_filtered['Value_Bucket'].value_counts().sort_index().reset_index()
value_dist.columns = ['Bucket', 'Count']

# Create bar chart
fig_value_dist = px.bar(value_dist, x='Bucket', y='Count',
                        title='customer - Distribution of Order Values',
                        labels={'Count': 'Number of Orders'})

# Create color list - purple for regular, bright magenta for $100+
colors = ['#7B2CBF'] * (len(value_dist) - 1) + ['#FF1493']

fig_value_dist.update_traces(
    marker=dict(color=colors),
    hovertemplate='%{x}<br>Orders: %{y}<extra></extra>'
)

fig_value_dist.update_layout(
    hovermode='x unified',
    showlegend=False,
    xaxis_title='',
    yaxis_title='',
    height=300,
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig_value_dist, use_container_width=True)


# Calculate metrics by customer type
customer_metrics = df_filtered.groupby('Customer_Type').agg({
    'Order_ID': 'count',
    'Net_Order_Value_USD': 'mean',
    'Gross_Profit_USD': 'sum'
}).reset_index()

customer_metrics.columns = ['Customer_Type', 'Orders', 'Avg_Value', 'Total_Profit']

# Fixed order (doesn't change based on filters)
customer_type_order = ['New', 'Returning', 'Loyal']
customer_metrics['Customer_Type'] = pd.Categorical(customer_metrics['Customer_Type'], 
                                                    categories=customer_type_order, 
                                                    ordered=True)
customer_metrics = customer_metrics.sort_values('Customer_Type')

# Color mapping for cards
color_map = {
    'New': '#7B2CBF',
    'Returning': '#FF1493',
    'Loyal': '#6C63FF'
}

# Layout: Pie chart on left, metrics on right
col_chart, col_metrics = st.columns([1, 1])

with col_chart:
    # Pie chart
    fig_customer = px.pie(customer_metrics,
                           values='Orders',
                            names='Customer_Type',
                            color_discrete_sequence=['#FF1493', '#6C63FF', '#7B2CBF'],
                          title='customer - Orders by Customer Type')
    fig_customer.update_traces(hovertemplate='%{label}: %{value:,} orders<extra></extra>')
    fig_customer.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
    st.plotly_chart(fig_customer, use_container_width=True)

with col_metrics:
    # Add spacing to align with pie chart
    st.markdown("<div style='margin-top: 160px;'></div>", unsafe_allow_html=True)
    
    # Metrics displayed horizontally (3 cards side by side)
    metric_cols = st.columns(len(customer_metrics))
    
    for metric_col, row in zip(metric_cols, customer_metrics.itertuples()):
        with metric_col:
            card_color = color_map[row.Customer_Type]
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; margin: 0 0 12px 0; color: {card_color};">{row.Customer_Type}</p>
                <p style="font-size: 11px; margin: 8px 0; color: {card_color};"><b>{int(row.Orders):,}</b> orders</p>
                <p style="font-size: 11px; margin: 8px 0; color: {card_color};"><b>${row.Avg_Value:.2f}</b> avg</p>
                <p style="font-size: 11px; margin: 8px 0; color: {card_color};"><b>${row.Total_Profit:,.0f}</b> profit</p>
            </div>
            """, unsafe_allow_html=True)

# OPERATIONS SECTION
st.markdown("---")
st.header("03. Operations") 
# DELIVERY EFFICIENCY (SCATTER: DISTANCE VS TIME)

# Create copy and map labels
df_plot = df_filtered.copy()
df_plot['On_Time_Label'] = df_plot['On_Time'].map({'Yes': 'On time', 'No': 'Late'})

# Layout: Scatter on left, pie on right
col_scatter, col_pie = st.columns([1, 1])

with col_scatter:
    # Scatter plot
    fig_efficiency = px.scatter(df_plot, 
                                x='Delivery_Distance_km', 
                                y='Delivery_Time_Min',
                                color='On_Time_Label',
                                title='ops - Time, distance and late deliveries',
                                labels={'Delivery_Distance_km': 'Distance (km)', 
                                       'Delivery_Time_Min': 'Time (minutes)',
                                       'On_Time_Label': 'Status'},
                                color_discrete_map={'On time': '#7B2CBF', 'Late': '#FF1493'})

    fig_efficiency.update_traces(hovertemplate='Distance: %{x:.2f} km<br>Time: %{y} min<extra></extra>')
    fig_efficiency.update_layout(showlegend=False)
    st.plotly_chart(fig_efficiency, use_container_width=True)

with col_pie:

    # Add spacing to push pie down
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    # Count On_Time values directly
    on_time_summary = df_filtered['On_Time'].value_counts().reset_index()
    on_time_summary.columns = ['Status', 'Count']
    
    # Map Yes/No to On time/Late
    on_time_summary['Status'] = on_time_summary['Status'].map({'Yes': 'On time', 'No': 'Late'})
    
    # Create pie
    fig_pie = px.pie(on_time_summary, values='Count', names='Status',
                     title='')
    
    # Manually set colors based on label
    colors = []
    for label in fig_pie.data[0].labels:
        if label == 'On time':
            colors.append('#7B2CBF')
        else:  # Late
            colors.append('#FF1493')
    
    fig_pie.update_traces(marker=dict(colors=colors),
                          hovertemplate='%{label}: %{value:,}<extra></extra>')
    fig_pie.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
    st.plotly_chart(fig_pie, use_container_width=True)


# DELIVERY DISTANCE DISTRIBUTION (STACKED BAR - FIXED BUCKETS)

# Create copy and map labels
df_hist = df_filtered.copy()
df_hist['On_Time_Label'] = df_hist['On_Time'].map({'Yes': 'On time', 'No': 'Late'})

# Create fixed buckets (1km intervals, 10+ at end)
bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, float('inf')]
labels = ['0-1 km', '1-2 km', '2-3 km', '3-4 km', '4-5 km', '5-6 km', '6-7 km', '7-8 km', '8-9 km', '9-10 km', '10+ km']

df_hist['Distance_Bucket'] = pd.cut(df_hist['Delivery_Distance_km'], bins=bins, labels=labels)
distance_dist = df_hist.groupby(['Distance_Bucket', 'On_Time_Label']).size().reset_index(name='Count')

# Create stacked bar chart
fig_distance = px.bar(distance_dist, x='Distance_Bucket', y='Count',
                      color='On_Time_Label',
                      title='ops - Distribution of Delivery Distances (Stacked)',
                      color_discrete_map={'On time': '#7B2CBF', 'Late': '#FF1493'},
                      barmode='stack')

# Style
fig_distance.update_traces(
    hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
)

fig_distance.update_layout(
    hovermode='x unified',
    showlegend=True,
    xaxis_title='',
    yaxis_title='',
    height=300,
    yaxis=dict(showgrid=False),
    legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5, title_text='')
)

st.plotly_chart(fig_distance, use_container_width=True)



# Layout: Peak time on left, scatter on right
col_peak, col_scatter = st.columns([1, 1])

# PEAK TIME ANALYSIS & ORDER VALUE VS DISTANCE

# Layout: Peak time on left, scatter on right
col_peak, col_scatter = st.columns([1.2, 1])

with col_peak:
    # Extract hour from Order_Time
    df_plot_time = df_filtered.copy()
    df_plot_time['Hour'] = pd.to_datetime(df_plot_time['Order_Time'], format='%H:%M').dt.hour
    df_plot_time['On_Time_Label'] = df_plot_time['On_Time'].map({'Yes': 'On time', 'No': 'Late'})

    # Group by hour and on_time status
    peak_time = df_plot_time.groupby(['Hour', 'On_Time_Label']).size().reset_index(name='Count')

    # Horizontal bar chart
    fig_peak = px.bar(peak_time, x='Count', y='Hour',
                      color='On_Time_Label',
                      title='ops - Orders by Hour (Peak Time)',
                      color_discrete_map={'On time': '#7B2CBF', 'Late': '#FF1493'},
                      barmode='stack',
                      orientation='h')

    fig_peak.update_traces(hovertemplate='Hour %{y}:00<br>Count: %{x}<extra></extra>')
    fig_peak.update_layout(
        showlegend=False,
        xaxis_title='',
        yaxis_title='',
        height=400,
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_peak, use_container_width=True)

with col_scatter:
    # Calculate orders per hour
    df_busy = df_filtered.copy()
    df_busy['Hour'] = pd.to_datetime(df_busy['Order_Time'], format='%H:%M').dt.hour
    
    hourly_orders = df_busy.groupby('Hour').size().reset_index(name='Orders')
    
    # Find busiest and least busy
    busiest = hourly_orders.loc[hourly_orders['Orders'].idxmax()]
    least_busy = hourly_orders.loc[hourly_orders['Orders'].idxmin()]
    
    # Add spacing to move down
    st.markdown("<div style='margin-top: 130px;'></div>", unsafe_allow_html=True)
    
    # Least Busy Hour card
    st.markdown(f"""
    <div style="text-align: center; padding: 3px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 10px;">
        <p style="font-size: 12px; margin: 0 0 2px 0; color: #666;">Least Busy Hour</p>
        <p style="font-size: 20px; font-weight: bold; margin: 0 0 2px 0; color: #333;">{int(least_busy['Hour']):02d}:00</p>
        <p style="font-size: 13px; margin: 0; color: #FF1493;"><b>↓ {int(least_busy['Orders'])} orders</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Busiest Hour card
    st.markdown(f"""
    <div style="text-align: center; padding: 3px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 10px;">
        <p style="font-size: 12px; margin: 0 0 2px 0; color: #666;">Busiest Hour</p>
        <p style="font-size: 20px; font-weight: bold; margin: 0 0 2px 0; color: #333;">{int(busiest['Hour']):02d}:00</p>
        <p style="font-size: 13px; margin: 0; color: #7B2CBF;"><b>↑ {int(busiest['Orders'])} orders</b></p>
    </div>
    """, unsafe_allow_html=True)
    



# RIDER PERFORMANCE ANALYSIS (SCATTER + ZONES)

# Calculate late % and order count by rider
rider_performance = df_filtered.groupby('Rider_ID').agg({
    'Order_ID': 'count',
    'On_Time': lambda x: (x == 'No').sum() / len(x) * 100
}).reset_index()
rider_performance.columns = ['Rider_ID', 'Deliveries', 'Late_Pct']

# Layout: Chart on left, cards on right

col_chart, col_cards = st.columns([1.2, 1])

with col_chart:
    # Create scatter plot
    fig_rider = px.scatter(rider_performance, 
                           x='Deliveries', 
                           y='Late_Pct',
                           title='ops - Rider Performance: Volume vs Late %',
                           labels={'Deliveries': 'Number of Deliveries',
                                  'Late_Pct': 'Late Delivery %'},
                           hover_data={'Rider_ID': True, 'Deliveries': True, 'Late_Pct': ':.1f'})

    fig_rider.update_traces(
        marker=dict(size=8, color='#7B2CBF'),
        hovertemplate='Rider %{customdata[0]}<br>Deliveries: %{x}<br>Late %: %{y:.1f}%<extra></extra>'
    )

    # Green zone (< 40%)
    fig_rider.add_shape(
        type="rect",
        x0=0, y0=0, x1=rider_performance['Deliveries'].max(), y1=40,
        fillcolor="#7B2CBF", opacity=0.5, layer="below",
        line=dict(width=0)
    )
    
    # Red zone (> 60%)
    fig_rider.add_shape(
        type="rect",
        x0=0, y0=60, x1=rider_performance['Deliveries'].max(), y1=100,
        fillcolor="#FF1493", opacity=0.5, layer="below",
        line=dict(width=0)
    )

    fig_rider.update_layout(
        height=400,
        xaxis_title='Number of Deliveries',
        yaxis_title='Late Delivery %',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    st.plotly_chart(fig_rider, use_container_width=True)

with col_cards:
    # Categorize riders by zone
    green_riders = len(rider_performance[rider_performance['Late_Pct'] < 40])
    yellow_riders = len(rider_performance[(rider_performance['Late_Pct'] >= 40) & (rider_performance['Late_Pct'] < 60)])
    red_riders = len(rider_performance[rider_performance['Late_Pct'] >= 60])
    total_riders = len(rider_performance)
    
    # Add spacing to align with chart
    st.markdown("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
    
    
    # Red Zone
    st.markdown(f"""
    <div style="text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 6px; min-height: 50px; display: flex; flex-direction: column; justify-content: center;">
        <p style="font-size: 10px; margin: 0 0 2px 0; color: #666;">Late Zone (> 60% late)</p>
        <div style="display: flex; justify-content: center; gap: 8px; align-items: center;">
            <p style="font-size: 14px; font-weight: bold; margin: 0; color: #FF1493;">{red_riders} riders</p>
            <p style="font-size: 13px; margin: 0; color: #FF1493;"><b>{(red_riders/total_riders)*100:.1f}%</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Yellow Zone
    st.markdown(f"""
    <div style="text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 6px; min-height: 50px; display: flex; flex-direction: column; justify-content: center;">
        <p style="font-size: 10px; margin: 0 0 2px 0; color: #666;">Regular Zone (40-60% late)</p>
        <div style="display: flex; justify-content: center; gap: 8px; align-items: center;">
            <p style="font-size: 14px; font-weight: bold; margin: 0; color: #666;">{yellow_riders} riders</p>
            <p style="font-size: 13px; margin: 0; color: #666;"><b>{(yellow_riders/total_riders)*100:.1f}%</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Green Zone
    st.markdown(f"""
    <div style="text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 6px; min-height: 50px; display: flex; flex-direction: column; justify-content: center;">
        <p style="font-size: 10px; margin: 0 0 2px 0; color: #666;">On time zone (< 40% late)</p>
        <div style="display: flex; justify-content: center; gap: 8px; align-items: center;">
            <p style="font-size: 14px; font-weight: bold; margin: 0; color: #7B2CBF;">{green_riders} riders</p>
            <p style="font-size: 13px; margin: 0; color: #7B2CBF;"><b>{(green_riders/total_riders)*100:.1f}%</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)