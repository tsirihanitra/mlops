pipeline {
    agent any

    environment {
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'nlp-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/tsirihanitra/mlops.git'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    python tests/test_predict.py
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build -t 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} \
                               192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Push to Harbor') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'harbor-credentials',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh """
                        docker login 192.168.43.55 -u \$USER -p \$PASS
                        docker push 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                        docker logout 192.168.43.55
                    """
                }
            }
        }

        stage('Clean up') {
            steps {
                sh """
                    docker rmi 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker rmi 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:latest || true
                """
            }
        }
    }

    post {
        success {
            echo "Image publiee : 192.168.43.55/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline echoue ! Verifiez les logs."
        }
        always {
            cleanWs()
        }
    }
}