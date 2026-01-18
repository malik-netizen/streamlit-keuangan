import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Family Finance Dashboard", page_icon="👨‍👩‍👧‍👦", layout="wide",)
st.title("👨‍👩‍👧‍👦 Family Finance Dashboard")

# =====================
# Get Data
# =====================

# Parameter
url = 'https://docs.google.com/spreadsheets/d/1xrI5_iL4B7Ue5TckMa86UxotsPWHwhySOEJ4BSkekc8/export?format=csv&gid=0'
df = pd.read_csv(url)

# st.dataframe(df)

# =====================
# Standarization Data
# =====================
df['date'] = pd.to_datetime(df['date'])
df_month = df[['month_int', 'month_str']].drop_duplicates().sort_values(['month_int'])

# =====================
# Filter
# =====================
st.sidebar.header("Filter")
months = st.sidebar.multiselect(
    "Bulan",
    df_month[['month_str']],
    default=df_month.iloc[-1]['month_str']
)

df1 = df[df['month_str'].isin(months)]

# =====================
# KPI
# =====================

cols = st.columns(4)

income = 8700000 + 15000000
expense = sum(df1["expense"])
saving = income - expense
saving_rate = (saving / income * 100) if income else 0
expected_saving_rate = 60
if saving_rate < expected_saving_rate:
    sign = "🔴"
    sign1 = "Bad"
elif saving_rate == 65:
    sign = "🟡"
    sign1 = "Warning"
else:
    sign = "🟢"
    sign1 = "Good"

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Income", f"Rp {income:,.0f}")
c2.metric("Expense", f"Rp {expense:,.0f}")
c3.metric("Saving", f"Rp {saving:,.0f}")
c4.metric("Saving Rate", f"{saving_rate:.0f}%")
c5.metric("Expected Saving Rate", f"{expected_saving_rate:.0f}%")
c6.metric(sign1, sign)

# =====================
# Cashflow
# =====================
# st.dataframe(df)
# monthly = df.groupby(['month', 'type'])['amount'].sum().reset_index()
# fig_cash = px.bar(
#     monthly,
#     x="month",
#     y="amount",
#     color="type",
#     barmode="group",
#     title="💵 Cashflow Bulanan"
# )
# st.plotly_chart(fig_cash, use_container_width=True)

# =====================
# Prepare Daily Expense Data
# =====================

daily_expense = (
    df
    .groupby(df['date'].dt.date)['expense']
    .sum()
    .reset_index()
    .rename(columns={'expense': 'Total Pengeluaran'})
)

daily_expense['date'] = pd.to_datetime(daily_expense['date'])

st.header("📉 Monitoring Pengeluaran Harian")

start_date, end_date = st.date_input(
    "Pilih rentang tanggal",
    value=[daily_expense['date'].min(), daily_expense['date'].max()]
)

filtered = daily_expense[
    (daily_expense['date'] >= pd.to_datetime(start_date)) &
    (daily_expense['date'] <= pd.to_datetime(end_date))
]

fig_filtered = px.line(
    filtered,
    x="date",
    y="Total Pengeluaran",
    markers=True,
    title="Pengeluaran Harian (Filtered)"
)

st.plotly_chart(fig_filtered, use_container_width=True)

max_day = filtered.loc[
    filtered['Total Pengeluaran'].idxmax()
]

st.warning(
    f"💸 Pengeluaran tertinggi terjadi pada "
    f"{max_day['date'].strftime('%d %B %Y')} "
    f"sebesar Rp {max_day['Total Pengeluaran']:,.0f}"
)

df_top5 = df[df['date'] == max_day['date']][['detail', 'expense', 'payment_tools']].sort_values(['expense'], ascending=False).reset_index(drop=True)
df_top5['expense'] = df_top5['expense'].apply(lambda x: f"Rp {x:,.0f}")
df_top5.columns = ['Item', 'Nominal', 'Payment']
st.dataframe(df_top5)