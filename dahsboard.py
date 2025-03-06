import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np

sns.set(style="dark")

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "total_revenue": "sum",
        "review_score": "mean"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_revenue": "revenue",
        "review_score" : "review_score"
    }, inplace=True)
    
    return daily_orders_df

def create_customer_reviews_df(df):
    avg_order_reviews_df = df.groupby("customer_satisfaction")["order_id"].nunique().reset_index()
    return avg_order_reviews_df

def create_total_order_product_df(df):
    total_order_product_df = df.groupby(by="product_id").order_id.nunique().sort_values(ascending=False).reset_index()
    return total_order_product_df

def create_total_order_state_df(df):
    total_order_state_df = df.groupby(by="customer_state").order_id.nunique().sort_values(ascending=False).reset_index()
    return total_order_state_df

all_sales_df = pd.read_csv("data/all_sales_df.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_sales_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_sales_df.reset_index(inplace=True)

for column in datetime_columns:
    all_sales_df[column] = pd.to_datetime(all_sales_df[column])


min_date = all_sales_df["order_purchase_timestamp"].min()
max_date = all_sales_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("assets\logo.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_sales_df[(all_sales_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_sales_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
byCustomer_Satisfaction_df = create_customer_reviews_df(main_df)
total_order_product_df = create_total_order_product_df(main_df)
total_order_state_df = create_total_order_state_df(main_df)

st.title(":red[E-COMMERCE] DASHBOARD :chart_with_upwards_trend:")

st.subheader("Daily Order")
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = daily_orders_df.revenue.sum()
    st.metric("Total Revenue", value=int(total_revenue))

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Customer Satisfaction")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    ax.pie(byCustomer_Satisfaction_df['order_id'], labels=byCustomer_Satisfaction_df['customer_satisfaction'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

with col2:
    total_revenue = daily_orders_df.review_score.mean()
    st.metric("Review Score Average", value=int(total_revenue))

st.subheader("Performa Terbaik dan Terburuk Produk")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_id", data=total_order_product_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Penjualan Produk", fontsize=30)
ax[0].set_title("Performa Terbaik Produk", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="order_id", y="product_id", data=total_order_product_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Penjualan Produk", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Performa Terburuk Produk", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader("Top 5 State dengan Penjualan Terbesar")

colors3 = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

top_5_states = total_order_state_df.head(5)
fig, ax = plt.subplots()
ax.bar(top_5_states['customer_state'], top_5_states['order_id'], color=colors3)
ax.set_xlabel('Negara Bagian Pelanggan')
ax.set_ylabel('Jumlah Pesanan')
ax.set_title('Jumlah Pesanan per Negara Bagian Pelanggan')
plt.xticks(rotation=45, ha='right') 
plt.tight_layout() 
st.pyplot(fig)