# 🚀 ReserveAI: End-to-End MLOps Pipeline for Room Reservation Prediction

<div align="center">
  <a href="https://ml-project-167836923927.us-central1.run.app/">
    <img src="https://img.shields.io/badge/LIVE_DEMO-Available_now!-brightgreen?style=for-the-badge&logo=google-chrome" alt="Live Demo">
  </a>
  
  <p>🚀 <strong>Production Environment:</strong> <a href="https://ml-project-167836923927.us-central1.run.app/">https://ml-project-167836923927.us-central1.run.app/</a></p>
</div>

## 🌟 Live Demo Features

```mermaid
graph LR
    A[Live Demo] --> B[Interactive Prediction]
    A --> C[API Documentation]
    A --> D[Sample Requests]
    A --> E[Performance Metrics]

Access these endpoints directly:

🖥️ Web Interface

📚 Swagger UI

📝 ReDoc

📊 Metrics

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![UV](https://img.shields.io/badge/uv-0.1.0-FFD43B?logo=pypi&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=googlecloud&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)

ReserveAI is a robust MLOps pipeline built with **Google Cloud Platform (GCP)** and a **custom Jenkins setup** that uses **Docker-in-Docker (DinD)** to build and deploy a machine learning model for predicting hotel room reservations.

---

## 📦 Features

- ✅ End-to-End Machine Learning Lifecycle
- ✅ Data pulled directly from Google Cloud Storage (GCS)
- ✅ Custom Jenkins CI/CD with Docker-in-Docker (DinD)
- ✅ Dockerized Flask API pushed to Google Container Registry (GCR)
- ✅ Scalable serverless deployment using Cloud Run

---

## 📁 Project Structure

![Architecture](architecture.png)

```bash
ReserveAI_MLOps_E2E/
│
├── pipeline/                 # Jenkins + Docker CI/CD scripts
├── config                    # Config file for configuration for model_params, paths
├── custom_jenkins/           # Jenkins-in-Docker configuration
├── src/                      # Model training and evaluation scripts
├── notebook/                 # EDA and prototyping notebooks
├── application.py            # Fast API serving predictions
├── templates                 # UI templates for serving predictions
├── Dockerfile                # Builds the Flask app image
├── Jenkinsfile               # CI/CD stages for Jenkins
├── pyproject.toml            # Application dependencies
└── README.md                 # Documentation


## Project Architecture 


## 🧠 Updated Architecture: GCP + Jenkins + Cloud Run
🔹 1. Data Ingestion
Training data is retrieved from Google Cloud Storage (GCS).

🔹 2. Model Training
Model is trained using Python, with output serialized (e.g., .pkl).

🔹 3. Custom Jenkins Setup
Jenkins runs inside Docker.

Docker-in-Docker (DinD) is used to:

Build the Docker image for the Flask API

Run all pipeline stages inside isolated containers

🔹 4. Docker Build
Flask API is containerized using a Dockerfile.

🔹 5. Push to GCR
Docker image is pushed to Google Container Registry (GCR).

🔹 6. Deployment to Cloud Run
Image is deployed to Google Cloud Run.

Exposes a public HTTP endpoint for model predictions.


## ⚙️ Tools & Services

Stage	Tool/Service
Data Storage	Google Cloud Storage (GCS)
CI/CD Orchestration	Jenkins (Docker-in-Docker)
Containerization	Docker
Image Registry	Google Container Registry (GCR)
Model Deployment	Google Cloud Run
API Framework	Flask
Language	Python

## 🚀 Quickstart Guide

1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yogeshkumarpilli/ReserveAI_MLOps_E2E.git
cd ReserveAI_MLOps_E2E


2. Set up Environment
bash
Copy
Edit
uv init
.venv/bin/activate
uv sync
uv build


## 🧪 Model Training
Ensure your GCP credentials are configured:

python
Copy
Edit
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('your-gcs-bucket')




# Download and load data
Then run:

bash
Copy
Edit
python pipeline/training.py




🐳 CI/CD with Jenkins (Docker-in-Docker)
Spin up Jenkins using the custom_jenkins Dockerfile

Ensure Docker socket is mounted for DinD

Jenkinsfile automates:

Linting and Testing

Docker Image Build

Push to GCR

Deployment to Cloud Run

📦 Build and Push to GCR
bash
Copy
Edit
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

docker build -t gcr.io/YOUR_PROJECT_ID/reserveai-api .
docker push gcr.io/YOUR_PROJECT_ID/reserveai-api


☁️ Deploy to Cloud Run
bash
Copy
Edit
gcloud run deploy reserveai-api \
  --image gcr.io/YOUR_PROJECT_ID/reserveai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated




image.png









🧪 Run Tests
bash
Copy
Edit
pytest tests/



📬 Contact
Yogesh Kumar Pilli
GitHub: @yogeshkumarpilli
Email: pilliyogeshkumar@example.com

📄 License
This project is licensed under the MIT License. See LICENSE for details.