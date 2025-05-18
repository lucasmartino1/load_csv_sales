"""
Carrega gs://data-engineer-project-lucas/raw/vendas.csv → BigQuery
Cria/atualiza a tabela dataset_vendas.tabela_vendas.
"""

from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

# ----- parâmetros que você pode querer mudar -------------
BUCKET            = "data-engineer-project-lucas"
OBJECT_PATH       = "raw/vendas.csv"
PROJECT_DATASET   = "skilled-torus-458514-i3.sales_dataset" 
DEST_TABLE        = f"{PROJECT_DATASET}.tabela_vendas"
GCP_CONN_ID       = "google_cloud_default"
# ----------------------------------------------------------

with DAG(
    dag_id="sales_csv_to_bq",
    start_date=datetime.now() - timedelta(days=1),
    schedule=None,
    catchup=False,
    tags=["gcp", "bigquery"],
) as dag:

    espera_arquivo = GCSObjectExistenceSensor(
        task_id="espera_vendas_csv",
        bucket=BUCKET,
        object=OBJECT_PATH,
        #gcp_conn_id=GCP_CONN_ID,  # Substituir google_cloud_conn_id por gcp_conn_id
        poke_interval=30,
        timeout=600,
    )

    carrega_bq = GCSToBigQueryOperator(
        task_id="load_csv_to_bq",
        bucket=BUCKET,
        source_objects=[OBJECT_PATH],
        destination_project_dataset_table=DEST_TABLE,
        #gcp_conn_id=GCP_CONN_ID,  # Substituir google_cloud_conn_id por gcp_conn_id
        schema_fields=[
            {"name": "name",        "type": "STRING"},
            {"name": "sale_id",     "type": "STRING"},
            {"name": "product_id",  "type": "INT64"},
            {"name": "product",     "type": "STRING"},
            {"name": "price_y",     "type": "FLOAT64"},
            {"name": "quantity",    "type": "FLOAT64"},
            {"name": "price_x",     "type": "FLOAT64"},
            {"name": "created_at",  "type": "TIMESTAMP"},
            {"name": "updated_at",  "type": "TIMESTAMP"},
            {"name": "email",       "type": "STRING"},
        ],
        source_format="CSV",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
    )

    espera_arquivo >> carrega_bq