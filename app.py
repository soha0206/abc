import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analytics Dashboard",
                   page_icon="📊",
                   layout="wide")

st.title("📊 Sales Analytics Dashboard")
st.markdown("Interactive dashboard using Streamlit")

uploaded = st.file_uploader("Upload CSV (Optional)", type="csv")

if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("data.csv")


money_cols = [
    "Cost Price",
    "Retail Price",
    "Sub Total",
    "Discount $",
    "Order Total",
    "Shipping Cost",
    "Total"
]

for col in money_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "Discount %" in df.columns:
    df["Discount %"] = (
        df["Discount %"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )
    df["Discount %"] = pd.to_numeric(df["Discount %"], errors="coerce")

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

df.drop_duplicates(inplace=True)
df.dropna(inplace=True)


st.sidebar.header("Filters")

state = st.sidebar.multiselect(
    "Select State",
    sorted(df["State"].unique()),
    default=sorted(df["State"].unique())
)

category = st.sidebar.multiselect(
    "Product Category",
    sorted(df["Product Category"].unique()),
    default=sorted(df["Product Category"].unique())
)

customer = st.sidebar.multiselect(
    "Customer Type",
    sorted(df["Customer Type"].unique()),
    default=sorted(df["Customer Type"].unique())
)

filtered = df[
    (df["State"].isin(state)) &
    (df["Product Category"].isin(category)) &
    (df["Customer Type"].isin(customer))
]


sales = filtered["Total"].sum()
orders = filtered.shape[0]
customers = filtered["Customer Name"].nunique()
avg = filtered["Total"].mean()
shipping = filtered["Shipping Cost"].sum()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Sales", f"${sales:,.2f}")
c2.metric("Orders", orders)
c3.metric("Customers", customers)
c4.metric("Average Order", f"${avg:,.2f}")
c5.metric("Shipping", f"${shipping:,.2f}")

st.divider()


st.subheader("Dataset")

st.dataframe(filtered, use_container_width=True)


monthly = (
    filtered
    .groupby(filtered["Order Date"].dt.to_period("M"))["Total"]
    .sum()
    .reset_index()
)

monthly["Order Date"] = monthly["Order Date"].astype(str)

fig = px.line(
    monthly,
    x="Order Date",
    y="Total",
    markers=True,
    title="Monthly Sales"
)

st.plotly_chart(fig, use_container_width=True)


state_sales = (
    filtered.groupby("State")["Total"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig = px.bar(
    state_sales,
    x="State",
    y="Total",
    title="Sales by State",
    color="Total"
)

st.plotly_chart(fig, use_container_width=True)


cat = (
    filtered.groupby("Product Category")["Total"]
    .sum()
    .reset_index()
)

fig = px.pie(
    cat,
    names="Product Category",
    values="Total",
    title="Category Contribution"
)

st.plotly_chart(fig, use_container_width=True)


top = (
    filtered.groupby("Product Name")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    top,
    x="Total",
    y="Product Name",
    orientation="h",
    title="Top 10 Products",
    color="Total"
)

st.plotly_chart(fig, use_container_width=True)


cust = (
    filtered["Customer Type"]
    .value_counts()
    .reset_index()
)

cust.columns = ["Customer Type", "Count"]

fig = px.bar(
    cust,
    x="Customer Type",
    y="Count",
    title="Customer Type Distribution"
)

st.plotly_chart(fig, use_container_width=True)


ship = (
    filtered["Ship Mode"]
    .value_counts()
    .reset_index()
)

ship.columns = ["Ship Mode", "Orders"]

fig = px.pie(
    ship,
    names="Ship Mode",
    values="Orders",
    title="Ship Mode"
)

st.plotly_chart(fig, use_container_width=True)


fig = px.scatter(
    filtered,
    x="Discount %",
    y="Total",
    color="Product Category",
    title="Discount vs Sales"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Summary")

st.write("Highest Sales State:", state_sales.iloc[0]["State"])
st.write("Best Product:", top.iloc[0]["Product Name"])
st.write("Total Revenue:", f"${sales:,.2f}")
st.write("Total Customers:", customers)


csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv,
    "Filtered_Sales.csv",
    "text/csv"
)