import os
from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import logging

HOST_PROJECT_ROOT = '/home/mirahasina/L3_INSI/DevOps_MLOps/mlops'

def train_model():
    logging.info("Training model inside Docker container...")
    result = subprocess.run(
        ["docker", "run", "--rm", 
         "-v", f"{HOST_PROJECT_ROOT}/src:/app/src", 
         "-v", f"{HOST_PROJECT_ROOT}/data:/app/data", 
         "-w", "/app",
         "mirahasina/wine-quality:latest", 
         "python", "src/train.py"],
        capture_output=True,
        text=True
    )
    logging.info(f"STDOUT: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"STDERR: {result.stderr}")
        raise Exception(f"Docker run failed with return code {result.returncode}")

def validate_model():
    logging.info("Validation du modèle...")

def deploy_model():
    logging.info("Starting deployment via Docker...")
    
    # 1. Stop existing container
    subprocess.run(["docker", "stop", "wine-prediction-app"], capture_output=True)
    subprocess.run(["docker", "rm", "wine-prediction-app"], capture_output=True)
    
    # 2. Start new container
    result = subprocess.run(
        ["docker", "run", "-d", 
         "--name", "wine-prediction-app",
         "-p", "5000:5000",
         "-v", f"{HOST_PROJECT_ROOT}/data:/app/data",
         "-v", f"{HOST_PROJECT_ROOT}/src:/app/src",
         "--network", "mlops_mlops-network",
         "--restart", "always",
         "mirahasina/wine-quality:latest"],
        capture_output=True,
        text=True
    )
    logging.info(f"STDOUT: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"STDERR: {result.stderr}")
        raise Exception(f"Docker run failed with return code {result.returncode}")

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
