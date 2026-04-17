pipeline {
    agent any

    environment {
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
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

        stage('Install dependencies') {
            steps {
                sh '''
                    apt-get update -y
                    apt-get install -y python3 python3-pip
                    python3 -m pip install --break-system-packages -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh 'python3 tests/test_predict.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build -t ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} \
                               ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Scan Trivy') {
            steps {
                sh '''
                    # Installer Trivy si pas encore present
                    if ! command -v trivy &> /dev/null; then
                        apt-get update -y
                        apt-get install -y wget apt-transport-https gnupg
                        wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
                        echo "deb https://aquasecurity.github.io/trivy-repo/deb generic main" > /etc/apt/sources.list.d/trivy.list
                        apt-get update -y
                        apt-get install -y trivy
                    fi
                '''
                sh """
                    # Scanner l image Docker
                    trivy image \
                        --exit-code 0 \
                        --severity LOW,MEDIUM,HIGH,CRITICAL \
                        --format table \
                        ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
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
                        docker login ${HARBOR_URL} -u \$USER -p \$PASS
                        docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                        docker logout ${HARBOR_URL}
                    """
                }
            }
        }

        stage('Clean up') {
            steps {
                sh """
                    docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest || true
                """
            }
        }
    }

    post {
        success {
            echo "Image publiee et scannee : ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline echoue ! Verifiez les logs."
        }
        always {
            cleanWs()
        }
    }
}
