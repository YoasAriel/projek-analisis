import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_yearly_orders_df(df):
    yearly_orders_df =df.resample(rule="MS", on="order_purchase_timestamp").agg({
    "price": "sum",
    "order_id": "nunique"
})
    yearly_orders_df["year"] = yearly_orders_df.index.year
    yearly_orders_df = yearly_orders_df.reset_index(drop=True)
    yearly_orders_df = yearly_orders_df.groupby(["year"]).agg({
    "price": "sum",
    "order_id": "sum"
    }).reset_index().rename(columns={
    "price": "value",
    "order_id": "order_count"
    })
    return yearly_orders_df

def create_sum_status_order_df(df):
    sum_status_order_df = df.groupby("order_status").price.sum().sort_values(ascending=False).reset_index()
    return sum_status_order_df.head(10)

def create_top10_category_name_english_df(df):
    top10_category_name_english_df = df.groupby("product_category_name_english").order_id.count().sort_values(ascending=False).reset_index()
    return top10_category_name_english_df

def create_bottom10_category_name_english_df(df):
    bottom10_category_name_english_df = df.groupby("product_category_name_english").order_id.count().sort_values(ascending=True).reset_index()
    return bottom10_category_name_english_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
    "order_id": "nunique",
    "price": "sum"
    })
    rfm_df.columns = ["customer_id", "order_purchase_timestamp", "frequency", "monetary"]
    rfm_df["order_purchase_timestamp"] = rfm_df["order_purchase_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)

    return rfm_df

# Load cleaned data
all_df = pd.read_csv("all_data.csv")
datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Period Time",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# st.dataframe(main_df)


# # Menyiapkan berbagai dataframe
yearly_orders_df = create_yearly_orders_df(main_df)
sum_status_order_df = create_sum_status_order_df(main_df)
top10_category_name_english_df = create_top10_category_name_english_df(main_df)
bottom10_category_name_english_df = create_bottom10_category_name_english_df(main_df)
rfm_df = create_rfm_df(main_df)


# Data
def home():
    st.header("Welcome to Dashboard")
    st.write("\"We are not what we know but what we are willing to learn.\"")
    st.write("\"Good people are good because they've come to wisdom through failure.\"")
    st.write("\"Your word is a lamp for my feet, a light for my path.\"")
    st.write("\"The first problem for all of us, men and women, is not to learn, but to unlearn.\"")

def data_visualization():
    st.header("Data Visualization")
    #Total Omset
    st.subheader("Total Revenue Yearly")
    col1, col2 = st.columns(2)
    with col1:
        plt.figure(figsize=(6, 4))
        plt.plot(
        yearly_orders_df["year"],
        yearly_orders_df["value"],
        marker="D",  
        markersize=8,  
        linewidth=2,  
        color="#88D66C",
        linestyle='-',  
        )
        plt.title("Total Omset per Tahun (Million)", loc="center", fontsize=14)
        plt.xlabel("Year", fontsize=12)  
        plt.ylabel("Value (Million)", fontsize=12)  
        plt.xticks(yearly_orders_df["year"], fontsize=10)  
        plt.yticks(fontsize=10)
        plt.grid(visible=True, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
        st.pyplot(plt.gcf())

    with col2:
        plt.figure(figsize=(8, 5))
        plt.bar(
        yearly_orders_df["year"],
        yearly_orders_df["value"],
        color="#88D66C",
        edgecolor="black"
        )
        plt.title("Total Omset per Tahun (Million)", loc="center", fontsize=20)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Value (Million)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        st.pyplot(plt.gcf())


    #Total Revenue by Status
    st.subheader("Total Revenue by Status")
    colors = ["#22d", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x="price", 
        y="order_status", 
        data=sum_status_order_df.sort_values(by="price", ascending=False).head(10), 
        palette=colors
    )
    plt.ylabel(None)
    plt.xlabel(None)
    plt.title("Total Price by Order Status", loc="center", fontsize=15)
    plt.tick_params(axis='y', labelsize=12)
    st.pyplot(plt.gcf())
    plt.clf()


    #Top 10
    st.subheader("Top 10 Orders by Product Category")
    plt.figure(figsize=(10,6))
    plt.bar(top10_category_name_english_df.sort_values(by="order_id", ascending=False).head(10)["product_category_name_english"], top10_category_name_english_df.sort_values(by="order_id", ascending=False).head(10)["order_id"], color="skyblue")
    plt.title("Top 10 Order by Product Category")
    plt.xlabel("Product Category")
    plt.ylabel("Total Orders")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(plt.gcf())


    #Bottom 10
    st.subheader("Bottom 10 Orders by Product Category")
    plt.figure(figsize=(10,6))
    plt.bar(bottom10_category_name_english_df.head(10)["product_category_name_english"], bottom10_category_name_english_df.head(10)["order_id"], color="skyblue")
    plt.title("Bottom 10 Order by Product Category")
    plt.xlabel("Product Category")
    plt.ylabel("Total Orders")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())


    #Top 10 vs Bottom 10
    st.subheader("Top 10 vs Bottom 10")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
    
    colors = ["#22d", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4","#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

    sns.barplot(x="order_id", y="product_category_name_english", data=top10_category_name_english_df.sort_values(by="order_id", ascending=False).head(10), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Top 10 Orders by Product Category", loc="center", fontsize=15)
    ax[0].tick_params(axis ='y', labelsize=12)
    
    sns.barplot(x="order_id", y="product_category_name_english", data=bottom10_category_name_english_df.sort_values(by="order_id", ascending=True).head(10), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Top 10 Bottom by Product Category", loc="center", fontsize=15)
    ax[1].tick_params(axis='y', labelsize=12)
    
    plt.suptitle("Total Orders by Product Category", fontsize=20)
    st.pyplot(plt.gcf())


    # Best Customer Based on RFM Parameters
    st.subheader("Best Customer Based on RFM Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)

    with col3:
        avg_frequency = format_currency(rfm_df.monetary.mean(), "$") 
        st.metric("Average Monetary", value=avg_frequency)
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    
    colors = ["#22d", "#22d", "#22d", "#22d", "#22d"]
    
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)
    
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)
    
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)
    
    plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
    st.pyplot(plt.gcf())



# Dashboard Title
st.title("E-Commerce Public Dashboard")

# Sidebar
st.sidebar.title("Menu")
menu = st.sidebar.radio("Pilih Halaman", ["Home", "Data Visualization"])
if menu == "Home":
    home()
elif menu == "Data Visualization":
    data_visualization()

# Footer
st.caption("Copyright © Yoas_Ariel 2024")
