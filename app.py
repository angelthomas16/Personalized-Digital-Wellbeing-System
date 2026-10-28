
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Digital Wellbeing Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Personalized Digital Wellbeing Dashboard")
st.markdown(
    "Monitor digital habits, personalized wellbeing scores, "
    "deviations, anomalies, and recommendations."
)

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent

# Use CSV files already tracked in the GitHub repository
DATA_PATH = ROOT / "notebooks" / "digital_wellbeing_scored.csv"
DAILY_PATH = ROOT / "notebooks" / "digital_wellbeing_cleaned.csv"

# Optional analytics summary
SUMMARY_PATH = ROOT / "results" / "user_summary.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Scored dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = [
        "user_id",
        "date",
        "daily_screen_time_hours",
        "sleep_hours",
        "physical_activity_minutes",
        "wellbeing_score",
        "flagged",
        "anomaly",
        "main_driver",
        "recommendation"
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    data["date"] = pd.to_datetime(
        data["date"], errors="coerce"
    )

    numeric_columns = [
        "wellbeing_score",
        "deviation",
        "daily_screen_time_hours",
        "social_media_hours",
        "gaming_hours",
        "work_study_hours",
        "sleep_hours",
        "notifications_per_day",
        "app_opens_per_day",
        "physical_activity_minutes",
        "flagged",
        "anomaly"
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column], errors="coerce"
            )

    data["flagged"] = data["flagged"].fillna(0).astype(int)
    data["anomaly"] = data["anomaly"].fillna(0).astype(int)

    # Merge baseline columns only when they exist.
    if DAILY_PATH.exists() and "record_id" in data.columns:
        daily = pd.read_csv(DAILY_PATH)

        baseline_columns = [
            "record_id",
            "daily_screen_time_hours_base",
            "sleep_hours_base",
            "physical_activity_minutes_base",
            "notifications_per_day_base"
        ]

        available = [
            column for column in baseline_columns
            if column in daily.columns
        ]

        if len(available) > 1:
            baseline_data = daily[available].drop_duplicates(
                subset=["record_id"]
            )

            data = data.merge(
                baseline_data,
                on="record_id",
                how="left",
                suffixes=("", "_baseline")
            )

    return data


try:
    df = load_data()

except Exception as error:
    st.error(f"Could not load analytics data: {error}")
    st.info(
        "Check that notebooks/digital_wellbeing_scored.csv "
        "exists in the GitHub repository and contains the "
        "required columns."
    )
    st.stop()


# --------------------------------------------------
# VALIDATE DATA
# --------------------------------------------------

df = df.dropna(subset=["user_id", "date"]).copy()

if df.empty:
    st.error("The dataset contains no valid user/date records.")
    st.stop()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

users = sorted(df["user_id"].astype(str).unique())

selected_user = st.sidebar.selectbox(
    "Select User",
    users
)

filtered_df = df[
    df["user_id"].astype(str) == selected_user
].copy()

available_years = sorted(
    filtered_df["date"].dt.year.dropna().unique().tolist()
)

if not available_years:
    st.error("No valid dates are available for this user.")
    st.stop()

selected_year = st.sidebar.selectbox(
    "Select Year",
    available_years,
    index=len(available_years) - 1
)

filtered_df = filtered_df[
    filtered_df["date"].dt.year == selected_year
].copy()

available_months = sorted(
    filtered_df["date"].dt.month.dropna().unique().tolist()
)

if available_months:
    month_options = ["All"] + available_months

    selected_month = st.sidebar.selectbox(
        "Select Month",
        month_options
    )

    if selected_month != "All":
        filtered_df = filtered_df[
            filtered_df["date"].dt.month == selected_month
        ].copy()

filtered_df = filtered_df.sort_values("date")

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------

st.subheader("Wellbeing Overview")

avg_score = filtered_df["wellbeing_score"].mean()
avg_screen = filtered_df["daily_screen_time_hours"].mean()
avg_sleep = filtered_df["sleep_hours"].mean()

flagged_count = filtered_df["flagged"].sum()
anomaly_count = filtered_df["anomaly"].sum()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Average Wellbeing Score",
    f"{avg_score:.2f}" if pd.notna(avg_score) else "N/A"
)

col2.metric(
    "Avg. Screen Time",
    f"{avg_screen:.2f} hrs" if pd.notna(avg_screen) else "N/A"
)

col3.metric(
    "Avg. Sleep",
    f"{avg_sleep:.2f} hrs" if pd.notna(avg_sleep) else "N/A"
)

col4.metric("Flagged Records", int(flagged_count))
col5.metric("Anomalies", int(anomaly_count))


# --------------------------------------------------
# WELLBEING SCORE TREND
# --------------------------------------------------

st.subheader("📈 Wellbeing Score Trend")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    filtered_df["date"],
    filtered_df["wellbeing_score"],
    marker="o",
    linewidth=1.5
)

ax.set_xlabel("Date")
ax.set_ylabel("Wellbeing Score")
ax.set_title("Daily Wellbeing Score")
ax.grid(True, alpha=0.3)

fig.autofmt_xdate()
st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# DIGITAL HABITS
# --------------------------------------------------

st.subheader("📱 Digital Habits")

habit_columns = [
    "daily_screen_time_hours",
    "social_media_hours",
    "gaming_hours",
    "work_study_hours"
]

available_habits = [
    column for column in habit_columns
    if column in filtered_df.columns
]

if available_habits:
    habit_data = (
        filtered_df.groupby("date")[available_habits]
        .mean()
    )

    st.line_chart(habit_data)
else:
    st.info("Digital habit columns are unavailable.")


# --------------------------------------------------
# SLEEP AND PHYSICAL ACTIVITY
# --------------------------------------------------

st.subheader("😴 Sleep and Physical Activity")

col1, col2 = st.columns(2)

with col1:
    if "sleep_hours" in filtered_df.columns:
        st.line_chart(
            filtered_df.set_index("date")[["sleep_hours"]]
        )

with col2:
    if "physical_activity_minutes" in filtered_df.columns:
        st.line_chart(
            filtered_df.set_index("date")[
                ["physical_activity_minutes"]
            ]
        )


# --------------------------------------------------
# DEVIATIONS AND ANOMALIES
# --------------------------------------------------

st.subheader("⚠️ Deviations and Anomalies")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Flagged deviations**")

    flagged_df = filtered_df[
        filtered_df["flagged"] == 1
    ]

    if flagged_df.empty:
        st.success("No flagged deviations in this selection.")
    else:
        display_columns = [
            column for column in [
                "date",
                "daily_screen_time_hours",
                "sleep_hours",
                "wellbeing_score",
                "deviation",
                "main_driver"
            ]
            if column in flagged_df.columns
        ]

        st.dataframe(
            flagged_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

with col2:
    st.markdown("**Detected anomalies**")

    anomaly_df = filtered_df[
        filtered_df["anomaly"] == 1
    ]

    if anomaly_df.empty:
        st.success("No anomalies in this selection.")
    else:
        display_columns = [
            column for column in [
                "date",
                "daily_screen_time_hours",
                "sleep_hours",
                "wellbeing_score",
                "main_driver"
            ]
            if column in anomaly_df.columns
        ]

        st.dataframe(
            anomaly_df[display_columns],
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# PERSONALIZED RECOMMENDATIONS
# --------------------------------------------------

st.subheader("💡 Personalized Recommendations")

recommendation_columns = [
    column for column in [
        "date",
        "wellbeing_score",
        "main_driver",
        "recommendation"
    ]
    if column in filtered_df.columns
]

recommendation_df = filtered_df[recommendation_columns].copy()

recommendation_df = recommendation_df.dropna(
    subset=["recommendation"]
)

if recommendation_df.empty:
    st.info("No recommendations are available for this selection.")
else:
    st.dataframe(
        recommendation_df.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# DAILY RECORDS
# --------------------------------------------------

st.subheader("📋 Daily Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------------------------

st.subheader("⬇️ Download Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="digital_wellbeing_filtered.csv",
    mime="text/csv"
)


# --------------------------------------------------
# OPTIONAL USER SUMMARY
# --------------------------------------------------

if SUMMARY_PATH.exists():
    st.subheader("📊 Analytics Summary")

    try:
        summary_df = pd.read_csv(SUMMARY_PATH)

        if "user_id" in summary_df.columns:
            summary_df = summary_df[
                summary_df["user_id"].astype(str) == selected_user
            ]

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as error:
        st.warning(f"Could not load optional summary: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Personalized Digital Wellbeing Intelligence System"
)
