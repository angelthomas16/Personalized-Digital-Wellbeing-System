from pathlib import Path
from pyspark.sql import SparkSession

project_dir = Path(__file__).resolve().parent.parent
hive_config = project_dir / "spark" / "conf"

spark = (
    SparkSession.builder
    .appName("SparkHiveConnectionTest")
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse")
    .config("spark.sql.catalogImplementation", "hive")
    .config("spark.hadoop.hive.metastore.uris", "thrift://localhost:9083")
    .config("spark.hadoop.hive.metastore.schema.verification", "false")
    .enableHiveSupport()
    .getOrCreate()
)

try:
    print("Databases visible to Spark:")
    spark.sql("SHOW DATABASES").show(truncate=False)

    print("Tables in hive_test:")
    spark.sql("SHOW TABLES IN hive_test").show(truncate=False)

    print("Sample rows from spark_daily_summary:")
    spark.sql(
        "SELECT * FROM hive_test.spark_daily_summary LIMIT 5"
    ).show(truncate=False)
finally:
    spark.stop()
