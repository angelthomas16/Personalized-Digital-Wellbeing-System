
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Digital Wellbeing Dashboard",
    page_icon="📱",
    layout="wide"
)

# Load the cleaned dataset
@st.cache_data
def load_data():
    data = pd.read_csv("notebooks/digital_wellbeing_cleaned.csv")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    return data

df = load_data()

# Dashboard heading
st.title("Personalized Digital Lifestyle and Wellbeing")
st.write(
    "Explore daily smartphone usage, sleep, physical activity, "
    "and personal usage patterns."
)

# Sidebar: user selection
st.sidebar.header("Personalized Analysis")

users = sorted(df["user_id"].dropna().unique().tolist())

if not users:
    st.error("No user records were found in the dataset.")
    st.stop()

selected_user = st.sidebar.selectbox(
    "Select User",
    users
)

user_df = df[df["user_id"] == selected_user].copy()
user_df = user_df.sort_values("date")

if user_df.empty:
    st.warning("No records are available for this user.")
    st.stop()

# Summary cards
st.header("Your Digital Lifestyle Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Daily Records", f"{len(user_df):,}")

col2.metric(
    "Average Screen Time",
    f"{user_df['daily_screen_time_hours'].mean():.2f} hours"
)

col3.metric(
    "Average Sleep",
    f"{user_df['sleep_hours'].mean():.2f} hours"
)

col4.metric(
    "Average Physical Activity",
    f"{user_df['physical_activity_minutes'].mean():.0f} min/day"
)

st.divider()

# Screen-time trend
st.subheader("1. Daily Screen-Time Trend")

fig1 = px.line(
    user_df,
    x="date",
    y="daily_screen_time_hours",
    markers=True,
    title="Daily Screen Time",
    labels={
        "date": "Date",
        "daily_screen_time_hours": "Screen Time (hours)"
    }
)

st.plotly_chart(fig1, use_container_width=True)

# Screen time and sleep relationship
st.subheader("2. Screen Time vs Sleep")

fig2 = px.scatter(
    user_df,
    x="daily_screen_time_hours",
    y="sleep_hours",
    hover_data=["date", "day_of_week"],
    title="Daily Screen Time and Sleep Duration",
    labels={
        "daily_screen_time_hours": "Screen Time (hours)",
        "sleep_hours": "Sleep (hours)"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# Daily activity comparison
st.subheader("3. Screen-Time Activity Breakdown")

activity_columns = [
    "social_media_hours",
    "gaming_hours",
    "work_study_hours"
]

activity_data = user_df[activity_columns].mean().reset_index()
activity_data.columns = ["Activity", "Average Hours"]

activity_data["Activity"] = activity_data["Activity"].map({
    "social_media_hours": "Social Media",
    "gaming_hours": "Gaming",
    "work_study_hours": "Work / Study"
})

fig3 = px.bar(
    activity_data,
    x="Activity",
    y="Average Hours",
    color="Activity",
    title="Average Daily Time by Activity"
)

st.plotly_chart(fig3, use_container_width=True)

# Sleep and physical activity trends
st.subheader("4. Sleep and Physical Activity")

sleep_activity = user_df[
    ["date", "sleep_hours", "physical_activity_minutes"]
].melt(
    id_vars="date",
    var_name="Measurement",
    value_name="Value"
)

sleep_activity["Measurement"] = sleep_activity["Measurement"].map({
    "sleep_hours": "Sleep (hours)",
    "physical_activity_minutes": "Physical Activity (minutes)"
})

fig4 = px.line(
    sleep_activity,
    x="date",
    y="Value",
    color="Measurement",
    markers=True,
    title="Daily Sleep and Physical Activity"
)

st.plotly_chart(fig4, use_container_width=True)

# Notifications and app openings
st.subheader("5. Digital Interaction Patterns")

interaction_data = user_df[
    ["date", "notifications_per_day", "app_opens_per_day"]
].melt(
    id_vars="date",
    var_name="Interaction",
    value_name="Count"
)

interaction_data["Interaction"] = interaction_data["Interaction"].map({
    "notifications_per_day": "Notifications",
    "app_opens_per_day": "App Opens"
})

fig5 = px.line(
    interaction_data,
    x="date",
    y="Count",
    color="Interaction",
    markers=True,
    title="Daily Notifications and App Opens"
)

st.plotly_chart(fig5, use_container_width=True)

# Personalized baseline comparison
st.subheader("6. Personal Usage Pattern")

average_screen = user_df["daily_screen_time_hours"].mean()
average_sleep = user_df["sleep_hours"].mean()

latest_record = user_df.dropna(subset=["date"]).sort_values("date")

if not latest_record.empty:
    latest = latest_record.iloc[-1]

    st.write(f"**Selected user:** {selected_user}")
    st.write(f"**Latest recorded date:** {latest['date'].strftime('%d %b %Y')}")

    screen_difference = (
        latest["daily_screen_time_hours"] - average_screen
    )
    sleep_difference = latest["sleep_hours"] - average_sleep

    col1, col2 = st.columns(2)

    col1.metric(
        "Latest Screen Time",
        f"{latest['daily_screen_time_hours']:.2f} hours",
        delta=f"{screen_difference:+.2f} hours vs personal average",
        delta_color="inverse"
    )

    col2.metric(
        "Latest Sleep",
        f"{latest['sleep_hours']:.2f} hours",
        delta=f"{sleep_difference:+.2f} hours vs personal average"
    )

    st.caption(
        "These comparisons use the selected user's average across the "
        "available records. They describe personal patterns and are not "
        "medical diagnoses or validated wellbeing risk scores."
    )

# Display daily records
st.subheader("7. Daily Usage Records")

display_columns = [
    "date",
    "day_of_week",
    "daily_screen_time_hours",
    "social_media_hours",
    "gaming_hours",
    "work_study_hours",
    "sleep_hours",
    "notifications_per_day",
    "app_opens_per_day",
    "physical_activity_minutes"
]

st.dataframe(
    user_df[display_columns],
    use_container_width=True,
    hide_index=True
)

# Download selected user's records
csv_data = user_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download This User's Data",
    data=csv_data,
    file_name=f"{selected_user}_digital_wellbeing.csv",
    mime="text/csv"
)

st.caption(
    "Dashboard based on the group's cleaned daily usage dataset. "
    "Patterns are descriptive and should not be interpreted as medical advice."
)
