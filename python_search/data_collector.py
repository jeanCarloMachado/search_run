import json
import os

class GenericDataCollector:
    """
    A generic data writer component that works tightly integrated with spark
    """

    BASE_DATA_DESTINATION_DIR = os.environ['HOME'] + "/.data/data_collection"

    @staticmethod
    def initialize():

        import fire
        return fire.Fire(GenericDataCollector())

    def write(self, *, data: dict, table_name: str, date=None):
        from datetime import datetime

        datetime.now().timestamp()

        import os

        os.system(f"mkdir -p {GenericDataCollector.BASE_DATA_DESTINATION_DIR}/{table_name}")
        import datetime

        file_name = f"{self.data_location(table_name)}/{datetime.datetime.now(datetime.timezone.utc).timestamp()}.json"

        with open(file_name, "w") as f:
            f.write(json.dumps(data))

        print(f"File {file_name} written successfully")

    def data_location(self, table_name):
        return f"{GenericDataCollector.BASE_DATA_DESTINATION_DIR}/{table_name}"

    def show_data(self, table_name):
        from pyspark.sql.session import SparkSession

        spark = SparkSession.builder.getOrCreate()

        df = spark.read.json(GenericDataCollector().data_location(table_name))
        df.show()


if __name__ == '__main__':
    GenericDataCollector.initialize()
