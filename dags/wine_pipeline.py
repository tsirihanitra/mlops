from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'tsirihanitra',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='wine_quality_pipeline',
    default_args=default_args,
    description='Pipeline MLOps Wine Quality',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    train = BashOperator(
        task_id='train_model',
        bash_command='python3 /opt/airflow/src/train.py',
    )

    test = BashOperator(
        task_id='test_model',
        bash_command='python3 /opt/airflow/src/predict.py',
    )

    build = BashOperator(
        task_id='docker_build',
        bash_command='docker build -t 192.168.43.53/mlops/wine-quality:latest /opt/airflow',
    )

    push = BashOperator(
        task_id='docker_push',
        bash_command='docker push 192.168.43.53/mlops/wine-quality:latest',
    )

    train >> test >> build >> push
