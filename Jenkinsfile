pipeline{
    agent any


    stages{

        stage('Cloning Github repo to Jenkins'){

            steps{
                
                script{
                    echo 'Cloning Github repo to Jenkins.....................'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github_token', url: 'https://github.com/yogeshkumarpilli/ReserveAI_MLOps_E2E.git']])
                }
            }
        }
    }
}