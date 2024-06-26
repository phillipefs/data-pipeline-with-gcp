from airflow import DAG
from airflow.utils.dates import days_ago, datetime
from airflow.operators.dummy import DummyOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable
import json
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateClusterOperator, \
    DataprocDeleteClusterOperator, DataprocSubmitJobOperator
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False
}

CLUSTER_NAME = 'stack-data-pipeline'
REGION = 'us-central1'
PROJECT_ID = 'datapipelines-419810'
CODE_BUCKET_NAME = 'data-pipeline-combustiveis-br-pyspark-code'
PYSPARK_FILE = 'main.py'

with DAG(
        dag_id="dag_fuel_load",
        default_args=default_args,
        description="Fuel data load dag",
        start_date=datetime(2009, 1, 1),
        schedule_interval=None,        
        # schedule_interval="0 0 1 */6 *",
        tags=["FUEL"],
        max_active_runs=1
        # catchup=False
) as dag:

    start_dag = DummyOperator(task_id="start_process")

    get_data = SimpleHttpOperator(
        task_id='get_file_to_bucket',
        method='POST',
        http_conn_id='stack-data-pipeline',
        endpoint='download_combustivel',
        # data=json.dumps({
        #     "bucket_name": "data-pipelines-combustiveis-br-raw",
        #     "url": "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-{{ dag_run.logical_date.strftime('%Y') }}-{{ '01' if dag_run.logical_date.month <= 6 else '02'}}.csv",
        #     "output_file_prefix": "combustiveis-brasil/{{ dag_run.logical_date.strftime('%Y') }}/{{ '01' if dag_run.logical_date.month <= 6 else '02'}}/ca-{{ dag_run.logical_date.strftime('%Y') }}-{{ '01' if dag_run.logical_date.month <= 6 else '02'}}.csv"
        # }),
        data=json.dumps({
            "bucket_name": "data-pipelines-combustiveis-br-raw",
            "url": "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2009-01.csv",
            "output_file_prefix": "combustiveis-brasil/2009/01/ca-2009-01.csv"
        }),
        headers={"Content-Type": "application/json"})

    CLUSTER_CONFIG = {
            "gce_cluster_config" : {
                "zone_uri": "us-central1-c"
            },
            "master_config": {
                "num_instances": 1,
                "machine_type_uri": "n1-standard-2",
                "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 50},
            },
            "worker_config": {
                "num_instances": 2,
                "machine_type_uri": "n1-standard-2",
                "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 50},
            },
        }

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
        cluster_name=CLUSTER_NAME)

    PYSPARK_JOB = {
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": {
            "main_python_file_uri": f"gs://{CODE_BUCKET_NAME}/{PYSPARK_FILE}",
            "jar_file_uris": ["gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar"],
            "args": [
                '--path_input',
                "gs://data-pipelines-combustiveis-br-raw/combustiveis-brasil/2009/01/ca-2009-01.csv",
                '--path_output',
                "gs://data-pipelines-combustiveis-br-curated/combustiveis-brasil/2009/01/",
                '--file_format', 'parquet',
                '--bq_dataset', 'gasolina_brasil',
                '--table_bq', 'tb_historico_combustivel_brasil'
            ]}
    }

    submit_job = DataprocSubmitJobOperator(
        task_id="spark_submit",
        job=PYSPARK_JOB,
        region=REGION,
        project_id=PROJECT_ID)

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
    )

    fim_dag = DummyOperator(task_id="end_process")

    start_dag >> get_data >> create_cluster >> submit_job >> delete_cluster >> fim_dag




