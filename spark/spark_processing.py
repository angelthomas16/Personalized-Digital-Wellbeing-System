import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, min as spark_min, max as spark_max
)

def main():
    # 1. Start Spark
    spark = (
        SparkSession.builder
        .appName("DigitalWellbeingProcessing")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    
    input_path = r"C:\Users\Arsha\Documents\Personalized-Digital-Wellbeing-System\notebooks\digital_wellbeing_cleaned.csv"

    output_path = r"C:\Users\Arsha\Documents\spark_output"

    # 2. Read the cleaned dataset
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(input_path)
    )

    print("Original row count:", df.count())

    # 3. Remove exact duplicate records
    df = df.dropDuplicates()

    # 4. Ensure the required columns are present
    required_columns = [
        "record_id", "user_id", "date",
        "daily_screen_time_hours", "social_media_hours",
        "gaming_hours", "work_study_hours", "sleep_hours",
        "notifications_per_day", "app_opens_per_day",
        "physical_activity_minutes"
    ]

    missing_columns = [
        name for name in required_columns
        if name not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 5. Remove rows without essential identifiers
    df = df.dropna(subset=["record_id", "user_id", "date"])

    # 6. Check numeric values
    numeric_columns = [
        "daily_screen_time_hours",
        "social_media_hours",
        "gaming_hours",
        "work_study_hours",
        "sleep_hours",
        "notifications_per_day",
        "app_opens_per_day",
        "physical_activity_minutes"
    ]

    for name in numeric_columns:
        df = df.withColumn(name, col(name).cast("double"))

    # Count records with missing numeric values
    missing_numeric_condition = None

    for name in numeric_columns:
        condition = col(name).isNull()
        missing_numeric_condition = (
            condition if missing_numeric_condition is None
            else missing_numeric_condition | condition
        )

    missing_numeric_count = df.filter(
        missing_numeric_condition
    ).count()

    print("Rows with missing numeric values:", missing_numeric_count)

    # 7. Exclude rows with missing or physically invalid values
    valid_condition = (
        col("daily_screen_time_hours").between(0, 24)
        & col("social_media_hours").between(0, 24)
        & col("gaming_hours").between(0, 24)
        & col("work_study_hours").between(0, 24)
        & col("sleep_hours").between(0, 24)
        & (col("notifications_per_day") >= 0)
        & (col("app_opens_per_day") >= 0)
        & col("physical_activity_minutes").between(0, 1440)
    )

    for name in numeric_columns:
        valid_condition = valid_condition & col(name).isNotNull()

    processed = df.filter(valid_condition)

    print("Valid rows after checks:", processed.count())

    # 8. Generate daily summaries for each user
    daily_summary = (
        processed
        .groupBy("user_id", "date")
        .agg(
            count("*").alias("record_count"),
            avg("daily_screen_time_hours").alias(
                "avg_screen_time_hours"
            ),
            avg("social_media_hours").alias(
                "avg_social_media_hours"
            ),
            avg("gaming_hours").alias("avg_gaming_hours"),
            avg("work_study_hours").alias("avg_work_study_hours"),
            avg("sleep_hours").alias("avg_sleep_hours"),
            avg("notifications_per_day").alias(
                "avg_notifications_per_day"
            ),
            avg("app_opens_per_day").alias("avg_app_opens_per_day"),
            avg("physical_activity_minutes").alias(
                "avg_physical_activity_minutes"
            )
        )
    )

    # 9. Save processed data and summaries
    os.makedirs(output_path, exist_ok=True)

    processed_file = os.path.join(
        output_path, "processed_data.csv"
    )

    summary_file = os.path.join(
        output_path, "daily_summary.csv"
    )

    print("Exporting processed data...")
    processed.toPandas().to_csv(
        processed_file, index=False
    )

    print("Exporting daily summaries...")
    daily_summary.toPandas().to_csv(
        summary_file, index=False
    )

    print("Processed data saved to:", processed_file)
    print("Daily summary saved to:", summary_file)

if __name__ == "__main__":
    main()
