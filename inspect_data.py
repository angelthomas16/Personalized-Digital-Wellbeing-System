
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("InspectLifestyleData")
    .master("local[*]")
    .getOrCreate()
)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("notebooks/digital_wellbeing_cleaned.csv")
)

print("=== DATA SCHEMA ===")
df.printSchema()

print("=== FIRST 5 ROWS ===")
df.show(5, truncate=False)

print("Total rows:", df.count())
print("Column names:", df.columns)

spark.stop()
