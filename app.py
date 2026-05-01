import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🎮 Gaming Dashboard")

df = pd.read_csv("Gaming_Academic_Performance.csv")

st.write("Dataset Preview")
st.dataframe(df.head())

fig = px.scatter(df, x="gaming_hours", y="grades")
st.plotly_chart(fig)