# QS-Promoter-Tool
import streamlit as st
import pandas as pd
import numpy as np

Title
st.title("🧬 Promoter Recommender Tool")

Load the Excel file
@st.cache_data
def load_data():
xls = pd.ExcelFile("data for qs software.xlsx")
gfp_df = xls.parse("GFP")
mcherry_df = xls.parse("mcherry")
time_df = xls.parse("time")

css
Copy
Edit
def time_str_to_minutes(time_str):
    try:
        h, m, s = map(int, str(time_str).split(':'))
        return h * 60 + m + s / 60
    except:
        return np.nan

time_numeric_df = time_df.set_index("Unnamed: 0").applymap(time_str_to_minutes)
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

Sidebar inputs
st.sidebar.header("Input Desired Expression")
desired_gfp = st.sidebar.number_input("Desired GFP", min_value=0.0, max_value=2.0, value=0.4)
desired_mcherry = st.sidebar.number_input("Desired mCherry", min_value=0.0, max_value=2.0, value=0.4)
desired_time = st.sidebar.number_input("Trigger Time (minutes)", min_value=0, max_value=600, value=200)

Scoring
df["diff_score"] = (
abs(df["GFP"] - desired_gfp) +
abs(df["mCherry"] - desired_mcherry) +
abs(df["TriggerTime_min"] - desired_time) / 60
)

Display top matches
st.subheader("🔍 Top Matching Promoter Combinations")
top = df.sort_values("diff_score").head(10)
st.dataframe(top[["Sender", "Receiver", "GFP", "mCherry", "TriggerTime_min", "diff_score"]])

Optional download
csv = top.to_csv(index=False)
st.download_button("📥 Download Results as CSV", csv, "top_matches.csv", "text/csv")
