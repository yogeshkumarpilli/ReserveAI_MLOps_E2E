pipeline {
    agent any

    environment {
        GCP_PROJECT = "spring-hope-458014-e6"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
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

        stage("Install Dependencies with UV") {
            steps {
                script {
                    echo 'Installing dependencies using uv...'
                    sh '''
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                        ~/.local/bin/uv venv
                        source .venv/bin/activate
                        uv sync
                        uv lock
                        uv build
                    '''
                }
            }
        }

        stage("Build & Push Docker Image to GCR") {
            steps {
                withCredentials([file(credentialsId: 'gcpkey', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Authenticating and pushing Docker image to GCR...'
                        sh '''
                            export PATH=$PATH:${GCLOUD_PATH}
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud auth configure-docker --quiet

                            # Copy creds to local file for Docker build
                            cp ${GOOGLE_APPLICATION_CREDENTIALS} ./temp_gcp_creds.json

                            docker build \
                                --build-arg GCP_KEY_JSON="$(cat ./temp_gcp_creds.json)" \
                                -t gcr.io/${GCP_PROJECT}/mlops-project:latest .

                            rm -f ./temp_gcp_creds.json

                            docker push gcr.io/${GCP_PROJECT}/mlops-project:latest
                        '''
                    }
                }
            }
        }

        stage("Train Model") {
            steps {
                script {
                    echo 'Running training pipeline...'
                    sh '''
                        source .venv/bin/activate
                        uv run pipeline/training.py
                    '''
                }
            }
        }

        stage("Cleanup Docker") {
            steps {
                script {
                    echo 'Cleaning up Docker image (optional)...'
                    sh 'docker rmi gcr.io/${GCP_PROJECT}/mlops-project:latest || true'
                }
            }
        }
    }
}
