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
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Scan Trivy') {
            steps {
                sh """
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v \$(pwd):/report \
                  aquasec/trivy:latest image \
                  --severity LOW,MEDIUM,HIGH,CRITICAL \
                  --format template \
                  --template "@contrib/html.tpl" \
                  -o /report/trivy-report.html \
                  ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Publish Trivy Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'trivy-report.html',
                    reportName: 'Trivy Security Report'
                ])
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'harbor-credentials',
                    usernameVariable: 'HARBOR_USER',
                    passwordVariable: 'HARBOR_PASS'
                )]) {
                    sh '''
                    echo "${HARBOR_PASS}" | docker login ${HARBOR_URL} \
                        -u "${HARBOR_USER}" --password-stdin
                    '''
                }
            }
        }

        stage('Docker Tag') {
            steps {
                sh """
                docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}

                docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Docker Push') {
            steps {
                sh """
                docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Clean up') {
            steps {
                sh """
                docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest || true
                """
            }
        }
    }

    post {
        success {
            echo "✅ Image publiée : ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ Pipeline échoué ! Vérifiez les logs."
        }
        always {
            cleanWs()
        }
    }
}
