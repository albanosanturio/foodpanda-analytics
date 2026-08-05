## Live Dashboard

🔗 **[View the Live Dashboard](https://share.streamlit.io/albanosanturio/foodpanda-analytics/main/app.py)**

*Dashboard is live and accessible online. All data loads from Kaggle API at runtime.*

## 🚀 Quick Links

- **Live Dashboard:** https://share.streamlit.io/albanosanturio/foodpanda-analytics/main/app.py
- **GitHub Repo:** https://github.com/albanosanturio/foodpanda-analytics
- **GitHub Repo:** https://albanosanturio.github.io/

# FoodPanda Analytics Dashboard

Interactive Streamlit dashboard analyzing delivery platform economics: profitability, operational efficiency, and customer behavior.

## Overview

This project explores FoodPanda order data to uncover business insights:
- **Where does the platform make money?** (by restaurant type, geography, order size)
- **What drives customer satisfaction?** (delivery performance, order value, discounts)
- **How efficient are operations?** (margins, delivery times, rider performance)


## Data

- **Source:** Kaggle ([FoodPanda Pakistan Customer Orders & Churn Dataset](https://www.kaggle.com/datasets/faheem113141/foodpanda-pakistan-customer-orders-and-churn-dataset))
- **Records:** 3,620 orders
- **Features:** 62 columns (orders, customers, restaurants, riders, financials, ratings)


Considerations for the analysis:

Keep in mind, as the kaggle website says, this is synthetically generated data, with realistic distributions and consistent financials.

On-time delivery threshold = 40 minutes.
Dataset has geoloc data, let's infer distance information.




## Tech Stack

- **Python** (Pandas, Plotly)
- **Streamlit** (dashboard framework)
- **Kaggle API** (data acquisition)

## Usage

Visit the dashboard, use filters (city, restaurant type, date range) to explore:
- Profitability by segment
- Delivery performance impact
- Customer value distribution
- Operations trends over time


## Key Findings

- Fine Dining: $16.51 profit/order × 234 orders = $3,863 total profit
- Fast Food: $11.01 profit/order × 1,754 orders = $19,315 total profit
- Fine Dining delivers 50% higher profit-per-order but Fast Food scales better
- Casual Dining: $13.21 profit/order × 1,178 orders = $15,561 total profit
- Profit margins stable 47–54% year-round
- Late-night margins (51.3%) ≈ regular hours (50.8%)
- Late-night cancellation rate: 11.1% vs regular: 10.1%
- Weekend late-night orders slightly higher than weekday
- Weekend avg order: $20.85 | Weekday: $20.70 (0.7% difference)
- No significant seasonal demand variation
- Restaurant category has minimal impact on delivery time (~40–42 min across all types)
- 29% of riders have >60% late delivery rate — operational risk
- Only 11% of riders achieve <40% late rate — high performers
- Higher cost Food Cost: 65.1% of total costs (primary cost driver)
- Second higher cost Rider Salary: 19.6%
- Loyal customers: $17,165 total profit (39.8% of orders)
- Returning customers: $16,891 total profit (39.3% of orders)
- New customers: $8,379 total profit (20.8% of orders)
- Avg ticket slightly higher on loyal customers
- Overall on-time rate: 40% | Late: 60%
- Distance does NOT strongly correlate with time


## Sketch

After exploratory analysis, decided on the following design:

```
┌────────────────────────────────────────────────────────────┐
│  FILTERS (Sidebar)                                         │
├────────────────────────────────────────────────────────────┤
│ Country: [Singapore, Pakistan, etc.]                       │
│ City: [Lahore, Singapore, etc.]                            │
│ Date Range: [Jan 1 - Dec 31]                               │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ MAIN DASHBOARD                                             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────┬──────────────┬────────────┬─────────────┐ │
│ │ Total Orders │ GMV $X       │ AOV $X     │ Margin %    │ │
│ │ (Volume)     │ (Total Rev)  │ (Avg Order)│ (Profitab.) │ │
│ └──────────────┴──────────────┴────────────┴─────────────┘ │
│                                                            │
│ === FINANCIALS ===                                         │
│ ┌─────────────────────────────────────────┐                │
│ │ Profitability by Category (Bar Chart)   │                │
│ │ [Fast Food | Casual | Fine Dining]      │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Cost Totals    (Line Chart)             │                │
│ │ Track cost total through time           │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Cost Breakdown (Pie Chart)              │                │
│ │ [Food | Rider | Marketing | Packaging]  │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ === CUSTOMER BEHAVIOUR ===                                 │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Order Value Distribution (Histogram)    │                │
│ │ Customer Segmentation                   │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Customer type behaviour                 │                │
│ │ Orders vs Customer Type                 │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ === OPERATIONS ===                                         │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Delivery Efficiency (Scatter)           │                │
│ │ Distance vs Time by City                │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Distance Distribution (Histogram)       │                │
│ │ Customer Segmentation                   │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
│ ┌─────────────────────────────────────────┐                │
│ │ Value vs Distance (scatter)             │                │
│ │ Time for money                          │                │
│ └─────────────────────────────────────────┘                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Future

- Deploy to Streamlit Cloud

---
