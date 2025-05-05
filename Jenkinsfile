pipeline {
    agent any

    environment {
        GCP_PROJECT = "spring-hope-458014-e6"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }
    
    parameters {
        booleanParam(
            defaultValue: false, 
            description: 'Run model training during deployment', 
            name: 'TRAIN_MODEL'
        )
        choice(
            choices: ['dev', 'staging', 'prod'], 
            description: 'Deployment environment', 
            name: 'DEPLOY_ENV'
        )
    }

    stages {
        stage("Clone Repository") {
            steps {
                script {
                    echo 'Cloning GitHub repository...'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github_token',
                            url: 'https://github.com/yogeshkumarpilli/ReserveAI_MLOps_E2E.git'
                        ]]
                    )
                }
            }
        }

        stage("Set Up Virtual Environment") {
            steps {
                script {
                    echo 'Setting up Virtual Environment and Installing dependencies...'
                    sh '''
                        # Install uv package manager
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                        . $HOME/.local/bin/env
                        
                        # Create and activate virtual environment
                        uv venv
                        . .venv/bin/activate
                        
                        # Install dependencies
                        uv sync
                        uv lock
                        uv build
                    '''
                }
            }
        }
        
        stage("Train Model (Optional)") {
            when {
                expression { return params.TRAIN_MODEL }
            }
            steps {
                withCredentials([file(credentialsId: 'gcpkey', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Training model...'
                        sh '''
                            # Activate virtual environment
                            . .venv/bin/activate
                            
                            # Set credentials and run training
                            export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
                            python pipeline/training.py
                            
                            # Save the model to artifacts directory
                            mkdir -p model_artifacts
                            cp -r models/* model_artifacts/ || echo "No models found"
                        '''
                    }
                }
            }
        }

        stage("Build & Push Docker Image") {
            steps {
                withCredentials([file(credentialsId: 'gcpkey', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Creating deployment scripts...'
                        // Create the entrypoint.sh file
                        sh '''
                            cat > entrypoint.sh << 'EOF'
#!/bin/bash
set -e

# Check if we need to train the model
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ -f "/app/data/sample_data.csv" ]; then
    echo "Starting model training..."
    python /app/pipeline/training.py
else
    echo "Skipping model training - no credentials or sample data found"
    echo "WARNING: Application may not work correctly without a trained model"
fi

# Run the application
echo "Starting the application..."
exec python /app/application.py
EOF
                            
                            # Make it executable
                            chmod +x entrypoint.sh
                            
                            # Create deployment script
                            cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

# This script safely mounts GCP credentials to the container
# Usage: ./deploy.sh <credentials_file> <project_id> [container_name]

CREDS_FILE=$1
PROJECT_ID=$2
CONTAINER_NAME=${3:-ml-service}
PORT=${PORT:-8000}

# Check inputs
if [ -z "$CREDS_FILE" ] || [ -z "$PROJECT_ID" ]; then
  echo "Usage: ./deploy.sh <credentials_file> <project_id> [container_name]"
  exit 1
fi

# Ensure credentials file exists
if [ ! -f "$CREDS_FILE" ]; then
  echo "Error: Credentials file not found at $CREDS_FILE"
  exit 1
fi

# Create a secure temp directory for credentials
CREDS_DIR=$(mktemp -d)
TEMP_CREDS="$CREDS_DIR/gcp-credentials.json"

# Copy credentials to temp file
cp "$CREDS_FILE" "$TEMP_CREDS"

# Deploy the container with credentials mounted
echo "Deploying container with mounted credentials..."
docker run -d \\
  --name $CONTAINER_NAME \\
  -p $PORT:8000 \\
  -v "$TEMP_CREDS:/app/gcp-credentials.json:ro" \\
  "gcr.io/$PROJECT_ID/ml-project:latest"

# Set up cleanup trap
cleanup() {
  echo "Cleaning up temporary credentials..."
  rm -rf "$CREDS_DIR"
}

trap cleanup EXIT

echo "Deployment complete! Service running at http://localhost:$PORT"
echo "Container logs:"
docker logs $CONTAINER_NAME
EOF
                            
                            chmod +x deploy.sh
                        '''
                        
                        echo 'Authenticating and building Docker image...'
                        sh '''
                            # Set up environment
                            export PATH=$PATH:${GCLOUD_PATH}
                            
                            # Authenticate with GCP
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud auth configure-docker --quiet

                            # Build Docker image
                            echo "Building Docker image..."
                            docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                            # Push to Google Container Registry
                            echo "Pushing Docker image..."
                            docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy (Optional)') {
            when {
                expression { return params.DEPLOY_ENV != null }
            }
            steps {
                withCredentials([file(credentialsId: 'gcpkey', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo "Preparing deployment for ${params.DEPLOY_ENV} environment..."
                        sh """
                            # Archive deployment assets
                            mkdir -p deployment/${params.DEPLOY_ENV}
                            cp deploy.sh deployment/${params.DEPLOY_ENV}/
                            cp ${GOOGLE_APPLICATION_CREDENTIALS} deployment/${params.DEPLOY_ENV}/gcp-credentials.json
                            
                            echo "Deployment package created for ${params.DEPLOY_ENV}."
                            echo "To deploy: cd deployment/${params.DEPLOY_ENV} && ./deploy.sh gcp-credentials.json ${GCP_PROJECT}"
                        """
                        
                        archiveArtifacts artifacts: "deployment/${params.DEPLOY_ENV}/**", fingerprint: true
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Please check the logs for details."
        }
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
    }
}