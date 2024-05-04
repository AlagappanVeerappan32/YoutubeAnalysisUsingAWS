import awswrangler as wr
import pandas as pd
import urllib.parse
import os

PATH_TO_S3_BUCKET = os.environ['s3_cleansed_layer']
DB_NAME = os.environ['glue_catalog_db_name']
TABLE_NAME = os.environ['glue_catalog_table_name']


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:

        # CONVERT TO DATAFRME
        df_raw = wr.s3.read_json('s3://{}/{}'.format(bucket, key))

        # Extract columns:
        df_step_1 = pd.json_normalize(df_raw['items'])

        # Write to S3
        wr_response = wr.s3.to_parquet(
            df=df_step_1,
            path=PATH_TO_S3_BUCKET,
            dataset=True,
            database=DB_NAME,
            table=TABLE_NAME,
            mode="APPEND"
        )
        return wr_response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}'.format(key, bucket))
        raise e
