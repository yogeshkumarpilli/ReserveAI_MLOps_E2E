pipeline{
    agent any

    environment {
        GCP_PROJECT = "spring-hope-458014-e6"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }


    stages{

        stage('Cloning Github repo to Jenkins'){

            steps{
                
                script{
                    echo 'Cloning Github repo to Jenkins.....................'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github_token', url: 'https://github.com/yogeshkumarpilli/ReserveAI_MLOps_E2E.git']])
                }
            }
        }

        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    . $HOME/.local/bin/env
                    uv venv
                    .venv/bin/activate
                    uv sync
                    uv lock
                    uv build
                    '''
                }
            }
        }
        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcpkey' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}


                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/mlops-project:latest .

                        docker push gcr.io/${GCP_PROJECT}/mlops-project:latest 

                        '''
                    }
                }
            }
        }
    }

}