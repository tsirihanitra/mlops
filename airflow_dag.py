import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import logging

PROJECT_ROOT = '/home/mirahasina/L3_INSI/DevOps_MLOps/mlops'

def run_script(script_path):
    logging.info(f"Running script: {script_path}")
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    logging.info(f"STDOUT: {result.stdout}")
    logging.error(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        raise Exception(f"Script {script_path} failed with return code {result.returncode}")

def train_model():
    run_script(os.path.join(PROJECT_ROOT, "src/train.py"))

def validate_model():
    logging.info("Validation du modèle...")

def deploy_model():
    logging.info("Starting deployment via Docker Compose (V2)...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    logging.info(f"STDOUT: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"STDERR: {result.stderr}")
        raise Exception(f"Docker compose failed with return code {result.returncode}")

with DAG(
    'wine_quality_mlops_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@weekly',
    catchup=False
) as dag:

    train = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )

    validate = PythonOperator(
        task_id='validate_model',
        python_callable=validate_model
    )

    deploy = PythonOperator(
        task_id='deploy_model',
        python_callable=deploy_model
    )

    train >> validate >> deploy
