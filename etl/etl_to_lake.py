"""

etl_to_lake

Migrate data from a SQL DB into a Data Lake in bulk.
Read from any SQL db with pandas and push the data into BigQuery tables.

Requires a list of tables and their ID columns for deduplication.

Requirements:
google-cloud-secret-manager
psycopg2
pandas-gbq
sqlalchemy


"""

import os
import pandas as pd
from google.cloud import secretmanager
import pandas_gbq


project_id = os.environ.get('PROJECT_ID')


def load_secrets(project_id, secret_id, version_id='latest'):
    """
    Load secrets from Google Secrets Manager
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    # If a Google Cloud environment isn't specified, skip this step.
    if project_id is None or secret_id is None:
        print(f'failed to load secrets for project={project_id} and secret_id={secret_id}')
        return
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    # Access the secret version.
    response = client.access_secret_version(request={"name": name})
    # Parse the secret payload. Should be one key=val pair per line
    payload = response.payload.data.decode("UTF-8")
    secrets = {line.split('=')[0]: line.split('=')[1] for line in payload.split('\n')}
    return secrets


def push_table_to_bq(table_df, bq_table, id_col):
    """
    Get the current IDs already in the remote db and remove them from the local table.
    Then push an update to bigquery.
    """
    sql = f"SELECT {id_col} FROM `{bq_table}`"
    # Get existing IDs to eliminate from the in-memory table
    try:
        gbq_df = pandas_gbq.read_gbq(sql, project_id=project_id)
        current_ids = set(gbq_df[id_col].tolist())
        table_df = table_df.loc[table_df[id_col].apply(lambda x: x not in current_ids), :]
    except Exception as err:
        if 'not found in location' in str(err):
            pass
        else:
            raise
    # If any data remains, sync it into the remote table
    if table_df.shape[0] > 0:
        pandas_gbq.to_gbq(table_df, destination_table=bq_table, project_id=project_id, if_exists="append")


def push_to_lake(request):
    """
    Push a batch of data to the data lake
    """
    secrets = load_secrets(project_id, 'etl-dev')
    # TODO - replace this with your desired tables+id_columns to ETL
    table_data = [{'name': 'user', 'id_col': 'id'},
                  {'name': 'order', 'id_col': 'order_id'},
                  {'name': 'post', 'id_col': 'id'}]
    for table_cfg in table_data:
        table = table_cfg['name']
        bq_table = f"{secrets['OUT_BQ_DATASET']}_lake.{table}"
        id_col = table_cfg['id_col']
        print({"table": table})
        try:
            table_df = pd.read_sql_table(table, secrets['DATABASE_URL'])
            if table == "user":
                table_df = table_df.drop(columns="password_hash")
            # Sort by timestamp if the option is available
            if "timestamp" in list(table_df.columns):
                table_df = table_df.sort_values(by=["timestamp"], ascending=False)
            if table_df.shape[0] > 0:
                print("migrating table: ", table)
                push_table_to_bq(table_df=table_df, bq_table=bq_table, id_col=id_col)
        except ValueError as err:
            print("ValueError:", err)
