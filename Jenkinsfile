pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "mlops-new-447207"
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
                    uv venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    uv build
                    '''
                }
            }
        }
    }
}