import pandas as pd
from geopy.distance import geodesic
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Load
df = pd.read_csv('data/foodpanda_raw.csv')  # wildcard in case filename varies

# Adding distance column (infering from latitude and longitude data)
df['Delivery_Distance_km'] = df.apply(
    lambda row: geodesic(
        (row['Restaurant_Latitude'], row['Restaurant_Longitude']),
        (row['Delivery_Latitude'], row['Delivery_Longitude'])
    ).km, axis=1
)

# Converting date to datetime format for slicing purposes
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Hour'] = pd.to_datetime(df['Order_Time'], format='%H:%M').dt.hour

# Creating 2 df, for weekdays and for weekends
weekday_df = df[df['Is_Weekend'] == 'No'].copy()
weekend_df = df[df['Is_Weekend'] == 'Yes'].copy()

# Creating 2 df, for late night and regular
early_df = df[df['Is_Late_Night_Order'] == 'No'].copy()
late_df = df[df['Is_Late_Night_Order'] == 'Yes'].copy()

# Count early vs late orders
weekday_early_late = weekday_df['Is_Late_Night_Order'].value_counts().reset_index()
weekday_early_late.columns = ['Time', 'count']
weekday_early_late['percentage'] = (weekday_early_late['count'] / weekday_early_late['count'].sum() * 100).round(1)

weekend_early_late = weekend_df['Is_Late_Night_Order'].value_counts().reset_index()
weekend_early_late.columns = ['Time', 'count']
weekend_early_late['percentage'] = (weekend_early_late['count'] / weekend_early_late['count'].sum() * 100).round(1)

# Rename for clarity
weekday_early_late['Time'] = weekday_early_late['Time'].map({'Yes': 'Late Night', 'No': 'Early/Regular'})
weekend_early_late['Time'] = weekend_early_late['Time'].map({'Yes': 'Late Night', 'No': 'Early/Regular'})



# Counting orders for each sub df
weekday_orders = weekday_df.groupby('Hour').size().reset_index(name='count')
weekend_orders = weekend_df.groupby('Hour').size().reset_index(name='count')


# Quick overview
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nFirst few rows:\n", df.head())
print("\nMissing values:\n", df.isnull().sum())
print("\nBasic stats:\n", df.describe(include='all'))
print("\nDuplicate rows:\n",df.duplicated().sum())
print("\n Value counts for 'product_category':\n",df['Product_Category'].value_counts())
print("\n Count unique values for 'product_category':\n",df['Product_Category'].nunique())
print("\n Value counts for 'product_name':\n",df['Product_Name'].value_counts())
print("\n Count unique values for 'product_name':\n",df['Product_Name'].nunique())
print("\n Value counts for 'Restaurant_Brand':\n",df['Restaurant_Brand'].value_counts())
print("\n Count unique values for 'Restaurant_Brand':\n",df['Restaurant_Brand'].nunique())

# Looking for insights
print("\n Profits per category: \n", df.groupby('Restaurant_Category')['Gross_Profit_USD'].agg(['sum', 'mean', 'count']))
print("\n Rating vs On time: \n", df.groupby('On_Time')['Customer_Rating'].mean())
print("\n net value: \n", df['Net_Order_Value_USD'].describe())

print("\n margin per day: \n", df.groupby(df['Order_Date'].dt.date)['Profit_Margin_Pct'].mean())

print("\n margin vs late night: \n", df.groupby(['Is_Late_Night_Order'])['Profit_Margin_Pct'].mean())

result_aux = df.groupby(['Is_Late_Night_Order','Order_Status']).size().reset_index(name='count')
result_aux['percentage'] = result_aux.groupby('Is_Late_Night_Order')['count'].transform(lambda x: (x / x.sum()) * 100)
print("\n Order Status and Late Night Grouping:\n", result_aux)

#print("\n order status and late night grouping: \n", df.groupby(['Is_Late_Night_Order','Order_Status']).size())
print("\n on time vs avg distance: \n", df.groupby(df['On_Time'])['Delivery_Distance_km'].mean())


# Calculate average spend on weekend and weekdays
weekday_avg = weekday_df['Net_Order_Value_USD'].mean()
weekend_avg = weekend_df['Net_Order_Value_USD'].mean()
difference = abs(weekend_avg - weekday_avg)
pct_diff = (difference / weekday_avg) * 100

# Print stats
print(f"\nWeekend vs Weekday Average Spend:")
print(f"Weekday avg spend: ${weekday_avg:.2f}")
print(f"Weekend avg spend: ${weekend_avg:.2f}")
print(f"Difference: ${difference:.2f} ({pct_diff:.1f}%)")

# Average delivery time by restaurant category
avg_time_by_category = df.groupby('Restaurant_Category')['Delivery_Time_Min'].mean().sort_values(ascending=False)
print("Average Delivery Time by Restaurant Category:")
print(avg_time_by_category)
print()

# Also get counts for context
time_stats = df.groupby('Restaurant_Category')['Delivery_Time_Min'].agg(['mean', 'count']).round(2)
print(time_stats)



df['Hour'] = pd.to_datetime(df['Order_Time'], format='%H:%M').dt.hour
fig = px.bar(df.groupby('Hour').size().reset_index(name='count'), x='Hour', y='count')
fig.update_layout(title="Orders by Hour of Day")
fig.show()


# Plot side-by-side orders per hour, weekday and weekends
fig = make_subplots(rows=1, cols=2, subplot_titles=('Weekday Orders', 'Weekend Orders'))

fig.add_trace(go.Bar(x=weekday_orders['Hour'], y=weekday_orders['count'], name='Weekday'), row=1, col=1)
fig.add_trace(go.Bar(x=weekend_orders['Hour'], y=weekend_orders['count'], name='Weekend'), row=1, col=2)

fig.update_xaxes(title_text='Hour', row=1, col=1)
fig.update_xaxes(title_text='Hour', row=1, col=2)
fig.update_yaxes(title_text='Orders', row=1, col=1)
fig.update_yaxes(title_text='Orders', row=1, col=2)

fig.show()

# Plot side-by-side orders late/regular on weekends or weekdays
fig = make_subplots(rows=1, cols=2, subplot_titles=('Weekday Orders', 'Weekend Orders'))

fig.add_trace(
    go.Bar(
        x=weekday_early_late['Time'], 
        y=weekday_early_late['count'],
        text=weekday_early_late['percentage'].astype(str) + '%',
        textposition='auto',
        name='Weekday'
    ), 
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=weekend_early_late['Time'], 
        y=weekend_early_late['count'],
        text=weekend_early_late['percentage'].astype(str) + '%',
        textposition='auto',
        name='Weekend'
    ), 
    row=1, col=2
)

fig.update_xaxes(title_text='Order Time', row=1, col=1)
fig.update_xaxes(title_text='Order Time', row=1, col=2)
fig.update_yaxes(title_text='Count', row=1, col=1)
fig.update_yaxes(title_text='Count', row=1, col=2)

fig.show()


""" 

Explore distincts
Product_Name Product_Category App_Platform App_Platform
Is_Late_Night_Order
Is_Weekend
 Columns to be dropped
Customer_Name  Customer_Phone 
Delivery_Address Restaurant_Founded 
Restaurant_Address Product_Name
App_Platform


Notes to analyze:

Margin by restaurang category 
Margin by late night order
Orders by day of the week
Orders by type of customer
Time vs rating
On_Time vs estimated_distance
Average order value
Cost breakdown (foodcost+packaging+rider+marketing, total and %)
Discount expenses

Weekend average spend
Weekend Hottest time windows

weekday average spend
Weekday Hottest time windows

Avg spend per cusstomer type

Late orders on weekdays vs weekends --> slightly higher on weekends

Skeleton Idea:
Slicer on left: Country, City, Time period
>main kpis section
>details on financials
>details on operations

 """