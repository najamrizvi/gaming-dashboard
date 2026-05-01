import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Gaming Dashboard", layout="wide")

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #141E30, #243B55);
    color: white;
}
h1, h2, h3 {
    color: #00FFD1;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SAFE DATA LOADER
# -----------------------------@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Gaming_Academic_Performance.csv")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Replace common nulls
    df.replace(["", "NA", "N/A", "null"], np.nan, inplace=True)

    # Convert to numeric safely
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        except:
            pass  # keep as is if completely non-numeric

    # Fill numeric NaNs
    for col in df.select_dtypes(include=np.number).columns:
        if df[col].isnull().all():
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna(df[col].median())

    # Fill categorical NaNs
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    return df

df = load_data()

if df.empty:
    st.stop()

# -----------------------------
# HEADER
# -----------------------------
st.title("🎮 Gaming vs Academic Dashboard")
st.subheader("Robust, Production-Safe Analytics")

# -----------------------------
# SIDEBAR FILTERS (AUTO)
# -----------------------------
st.sidebar.header("Filters")

filters = {}
for col in df.select_dtypes(include="object").columns:
    options = df[col].dropna().unique()
    if len(options) > 1:
        filters[col] = st.sidebar.multiselect(col, options, options)

filtered_df = df.copy()
for col, values in filters.items():
    if len(values) > 0:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

# -----------------------------
# KPI SECTION
# -----------------------------
st.markdown("## 📊 Key Metrics")

num_cols = filtered_df.select_dtypes(include=np.number).columns

cols = st.columns(min(4, len(num_cols)))

for i, col in enumerate(num_cols[:4]):
    value = filtered_df[col].mean() if len(filtered_df) > 0 else 0
    cols[i].metric(col.replace("_", " ").title(), f"{value:.2f}")

# -----------------------------
# SAFE PLOT FUNCTION
# -----------------------------
def safe_plot(plot_func):
    try:
        plot_func()
    except Exception as e:
        st.warning("⚠️ Chart could not be rendered due to data issues.")

# -----------------------------
# SAFE DATA PREP
# -----------------------------
def prepare_data(df, required_cols, positive_cols=None):
    temp = df.copy()

    for col in required_cols:
        if col not in temp.columns:
            return pd.DataFrame()

        temp[col] = pd.to_numeric(temp[col], errors="coerce")

    temp = temp.dropna(subset=required_cols)

    if positive_cols:
        for col in positive_cols:
            temp = temp[temp[col] > 0]

    return temp

# -----------------------------
# CHARTS
# -----------------------------
st.markdown("## 📈 Visual Insights")

col1, col2 = st.columns(2)

# Scatter 1
with col1:
    def plot1():
        temp = prepare_data(filtered_df, ["gaming_hours", "grades"], ["gaming_hours"])

        if len(temp) == 0:
            st.info("No valid data")
            return

        fig = px.scatter(
            temp,
            x="gaming_hours",
            y="grades",
            color="stress_level" if "stress_level" in temp.columns else None,
            size="addiction_score" if "addiction_score" in temp.columns else None,
            title="Gaming Hours vs Grades"
        )
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot1)

# Scatter 2
with col2:
    def plot2():
        temp = prepare_data(filtered_df, ["study_hours", "grades"])

        if len(temp) == 0:
            st.info("No valid data")
            return

        fig = px.scatter(
            temp,
            x="study_hours",
            y="grades",
            color="gender" if "gender" in temp.columns else None,
            title="Study Hours vs Grades"
        )
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot2)

# Row 2
col1, col2 = st.columns(2)

# Box plot
with col1:
    def plot3():
        if "gaming_genre" not in filtered_df or "grades" not in filtered_df:
            return

        fig = px.box(
            filtered_df,
            x="gaming_genre",
            y="grades",
            color="gaming_genre",
            title="Grades by Genre"
        )
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot3)

# Histogram
with col2:
    def plot4():
        temp = prepare_data(filtered_df, ["gaming_hours"])

        if len(temp) == 0:
            return

        fig = px.histogram(temp, x="gaming_hours", nbins=20)
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot4)

# Row 3
col1, col2 = st.columns(2)

# Pie
with col1:
    def plot5():
        if "gaming_genre" not in filtered_df:
            return

        fig = px.pie(filtered_df, names="gaming_genre")
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot5)

# Sleep vs Grades
with col2:
    def plot6():
        temp = prepare_data(filtered_df, ["sleep_hours", "grades"])

        if len(temp) == 0:
            return

        fig = px.scatter(temp, x="sleep_hours", y="grades")
        st.plotly_chart(fig, use_container_width=True)

    safe_plot(plot6)

# -----------------------------
# HEATMAP
# -----------------------------
st.markdown("## 🔥 Correlation Heatmap")

def plot_heatmap():
    num_df = filtered_df.select_dtypes(include=np.number)

    if num_df.empty:
        return

    corr = num_df.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        zmin=-1,
        zmax=1
    ))

    st.plotly_chart(fig, use_container_width=True)

safe_plot(plot_heatmap)

# -----------------------------
# DATA PREVIEW
# -----------------------------
st.markdown("## 📄 Data Preview")
st.dataframe(filtered_df.head(100))

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("✅ Fully Production-Safe Dashboard")
