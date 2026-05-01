import streamlit as st
import pandas as pd
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
# CLEAN UI
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
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Gaming_Academic_Performance.csv")
    df.columns = df.columns.str.strip().str.lower()

    # Handle missing values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(df[col].median())

    return df

df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.title("🎮 Gaming vs Academic Performance Dashboard")
st.subheader("Analyze how gaming habits affect student performance")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

gender = st.sidebar.multiselect(
    "Gender",
    df["gender"].unique(),
    df["gender"].unique()
)

genre = st.sidebar.multiselect(
    "Gaming Genre",
    df["gaming_genre"].unique(),
    df["gaming_genre"].unique()
)

stress = st.sidebar.multiselect(
    "Stress Level",
    df["stress_level"].unique(),
    df["stress_level"].unique()
)

filtered_df = df[
    (df["gender"].isin(gender)) &
    (df["gaming_genre"].isin(genre)) &
    (df["stress_level"].isin(stress))
]

# -----------------------------
# KPIs
# -----------------------------
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎮 Avg Gaming Hours", f"{filtered_df['gaming_hours'].mean():.2f}")
col2.metric("📚 Avg Study Hours", f"{filtered_df['study_hours'].mean():.2f}")
col3.metric("📈 Avg Grades", f"{filtered_df['grades'].mean():.2f}")
col4.metric("⚠️ Avg Addiction Score", f"{filtered_df['addiction_score'].mean():.2f}")

# -----------------------------
# CHARTS
# -----------------------------
st.markdown("## 📈 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        filtered_df,
        x="gaming_hours",
        y="grades",
        color="stress_level",
        size="addiction_score",
        title="Gaming Hours vs Grades"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        filtered_df,
        x="study_hours",
        y="grades",
        color="gender",
        title="Study Hours vs Grades"
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 2
col1, col2 = st.columns(2)

with col1:
    fig = px.box(
        filtered_df,
        x="gaming_genre",
        y="grades",
        color="gaming_genre",
        title="Grades by Gaming Genre"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        filtered_df,
        x="gaming_hours",
        nbins=20,
        title="Gaming Hours Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 3
col1, col2 = st.columns(2)

with col1:
    fig = px.pie(
        filtered_df,
        names="gaming_genre",
        title="Genre Popularity"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        filtered_df,
        x="sleep_hours",
        y="grades",
        color="stress_level",
        title="Sleep vs Grades"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# HEATMAP
# -----------------------------
st.markdown("## 🔥 Correlation Heatmap")

corr = filtered_df.corr(numeric_only=True)

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
st.markdown("🚀 Built with Streamlit & Plotly")
