import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Gaming vs Academic Dashboard",
    layout="wide"
)

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
h1, h2, h3 {
    color: #00FFD1;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD & CLEAN DATA (SAFE)
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Gaming_Academic_Performance.csv")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Expected columns
    numeric_cols = ["gaming_hours", "study_hours", "grades", "sleep_hours", "addiction_score"]
    cat_cols = ["gender", "gaming_genre", "stress_level"]

    # Convert numeric safely
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fill numeric NaNs
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Fill categorical NaNs
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df

df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.title("🎮 Gaming vs Academic Performance Dashboard")
st.subheader("Analyze how gaming habits affect academic performance")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

def safe_multiselect(column, label):
    if column in df.columns:
        return st.sidebar.multiselect(label, df[column].unique(), df[column].unique())
    return []

gender = safe_multiselect("gender", "Gender")
genre = safe_multiselect("gaming_genre", "Gaming Genre")
stress = safe_multiselect("stress_level", "Stress Level")

filtered_df = df.copy()

if "gender" in df.columns:
    filtered_df = filtered_df[filtered_df["gender"].isin(gender)]
if "gaming_genre" in df.columns:
    filtered_df = filtered_df[filtered_df["gaming_genre"].isin(genre)]
if "stress_level" in df.columns:
    filtered_df = filtered_df[filtered_df["stress_level"].isin(stress)]

# -----------------------------
# KPIs
# -----------------------------
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

def safe_mean(col):
    return f"{filtered_df[col].mean():.2f}" if col in filtered_df else "N/A"

col1.metric("🎮 Avg Gaming Hours", safe_mean("gaming_hours"))
col2.metric("📚 Avg Study Hours", safe_mean("study_hours"))
col3.metric("📈 Avg Grades", safe_mean("grades"))
col4.metric("⚠️ Avg Addiction Score", safe_mean("addiction_score"))

# -----------------------------
# CLEAN DATA FOR PLOTTING
# -----------------------------
plot_df = filtered_df.copy()

needed_cols = ["gaming_hours", "grades", "addiction_score"]
existing_cols = [col for col in needed_cols if col in plot_df.columns]

if existing_cols:
    plot_df = plot_df.dropna(subset=existing_cols)

# -----------------------------
# CHARTS
# -----------------------------
st.markdown("## 📈 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    if all(col in plot_df.columns for col in ["gaming_hours", "grades"]):
        fig = px.scatter(
            plot_df,
            x="gaming_hours",
            y="grades",
            color="stress_level" if "stress_level" in plot_df else None,
            size="addiction_score" if "addiction_score" in plot_df else None,
            title="Gaming Hours vs Grades"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if all(col in plot_df.columns for col in ["study_hours", "grades"]):
        fig = px.scatter(
            plot_df,
            x="study_hours",
            y="grades",
            color="gender" if "gender" in plot_df else None,
            title="Study Hours vs Grades"
        )
        st.plotly_chart(fig, use_container_width=True)

# Row 2
col1, col2 = st.columns(2)

with col1:
    if all(col in plot_df.columns for col in ["gaming_genre", "grades"]):
        fig = px.box(
            plot_df,
            x="gaming_genre",
            y="grades",
            color="gaming_genre",
            title="Grades by Gaming Genre"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "gaming_hours" in plot_df.columns:
        fig = px.histogram(
            plot_df,
            x="gaming_hours",
            nbins=20,
            title="Gaming Hours Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# Row 3
col1, col2 = st.columns(2)

with col1:
    if "gaming_genre" in plot_df.columns:
        fig = px.pie(
            plot_df,
            names="gaming_genre",
            title="Genre Popularity"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if all(col in plot_df.columns for col in ["sleep_hours", "grades"]):
        fig = px.scatter(
            plot_df,
            x="sleep_hours",
            y="grades",
            color="stress_level" if "stress_level" in plot_df else None,
            title="Sleep vs Grades"
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# HEATMAP
# -----------------------------
st.markdown("## 🔥 Correlation Heatmap")

numeric_df = plot_df.select_dtypes(include=np.number)

if not numeric_df.empty:
    corr = numeric_df.corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu",
            zmin=-1,
            zmax=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.markdown("## 📄 Dataset Preview")
st.dataframe(filtered_df.head(100))

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("🚀 Built with Streamlit & Plotly | Stable Version")
