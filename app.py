import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

st.set_page_config(page_title="Promoter Recommender Tool", layout="wide")
st.title("Promoter Recommender Tool For Lux QS-Co culture")
st.markdown("""
### ℹ️ How to Use This Tool

This tool helps you choose the best promoter combinations for quorum sensing (QS) based gene expression using a synthetic co-culture of two engineered E. coli strains.

- **Sender**: The cell expressing LuxI (and GFP) under a given promoter.
- **Receiver**: The cell expressing LuxR (and mCherry) under another promoter.

You provide your desired expression values:
- **GFP**: Expression level of the sender cell (Green Fluorescent Protein).
- **mCherry**: Expression level of the receiver cell (Red Fluorescent Protein).
- **Trigger Time**: Time (in minutes) after which the mCherry gene starts to express (triggered by AHL quorum sensing molecule).
- **Output**
- **3D Scatter Plot**: Visualizes promoter combinations based on GFP, mCherry, and Trigger Time. You can explore how close each point is to your input.
- **2D Plot**: Highlights the top few matching combinations — easy to compare expression levels and timing visually.
- **Table of Top Matches**: Lists promoter combinations with expression values and a `diff_score`. Lower score = closer match to your desired input.
- **diff_score**: This score quantifies how close each promoter combination is to your desired GFP, mCherry, and trigger time values — lower scores indicate a better match.
Use this to guide promoter design for synthetic co-cultures!



The app recommends combinations of promoters that best match your input, based on experimental data from 81 combinations.
**This Tool has been developed by protein and organism engineering lab IISER Kolkata**

""")


# Load Excel data
@st.cache_data
def load_data():
    xls = pd.ExcelFile("data for qs software.xlsx")
    gfp_df = xls.parse("GFP")
    mcherry_df = xls.parse("mcherry")
    time_df = xls.parse("time")

    def time_to_minutes(t):
        try:
            h, m, s = map(int, str(t).split(':'))
            return h * 60 + m + s / 60
        except:
            return np.nan

    time_numeric_df = time_df.set_index("Unnamed: 0").applymap(time_to_minutes)
    gfp_numeric_df = gfp_df.set_index("Unnamed: 0")
    mcherry_numeric_df = mcherry_df.set_index("Unnamed: 0")

    df_long = pd.DataFrame({
        "Receiver": np.repeat(gfp_numeric_df.index, len(gfp_numeric_df.columns)),
        "Sender": list(gfp_numeric_df.columns) * len(gfp_numeric_df.index),
        "GFP": gfp_numeric_df.values.flatten(),
        "mCherry": mcherry_numeric_df.values.flatten(),
        "TriggerTime_min": time_numeric_df.values.flatten()
    })
    return df_long

df = load_data()

# Sidebar inputs
st.sidebar.header("Desired Expression Inputs")
desired_gfp = st.sidebar.number_input("Desired GFP", 0.0, 2.0, 0.4)
desired_mcherry = st.sidebar.number_input("Desired mCherry", 0.0, 2.0, 0.4)
desired_time = st.sidebar.number_input("Trigger Time (min)", 0.0, 400.0, 200.0)

# Compute difference score
df["diff_score"] = (
    abs(df["GFP"] - desired_gfp) +
    abs(df["mCherry"] - desired_mcherry) +
    abs(df["TriggerTime_min"] - desired_time) / 60  # normalized
)

top = df.sort_values("diff_score").head(10)

# Display table
st.subheader("🔍 Top Matching Promoter Combinations")
st.dataframe(top[["Sender", "Receiver", "GFP", "mCherry", "TriggerTime_min", "diff_score"]])

# Bar chart of top scores
st.subheader("📊 Top 10 Combinations by Score")
bar_chart = alt.Chart(top).mark_bar().encode(
    x=alt.X("Sender:N", title="Sender"),
    y=alt.Y("diff_score:Q", title="Diff Score"),
    color="Receiver:N",
    tooltip=["Sender", "Receiver", "GFP", "mCherry", "TriggerTime_min", "diff_score"]
).properties(width=700, height=400)
st.altair_chart(bar_chart, use_container_width=True)

# 3D Scatter plot
st.subheader("🧬 3D Expression Profile (GFP, mCherry, Time)")
fig = px.scatter_3d(
    top,
    x="GFP",
    y="mCherry",
    z="TriggerTime_min",
    color="diff_score",
    hover_data=["Sender", "Receiver"],
    title="Top 10 Expression Combinations"
)
st.plotly_chart(fig, use_container_width=True)
