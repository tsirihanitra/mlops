pipeline {
    agent any

    environment {
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        // Définition des chemins pour Trivy
        REPORT_DIR     = "${env.WORKSPACE}/trivy-reports"
        TRIVY_CACHE    = "${env.WORKSPACE}/trivy-cache"
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
                sh 'python3 -m pip install --break-system-packages -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'python3 tests/test_predict.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

       stage('Security Scan (Trivy)') {
    steps {
        echo "Analyse de sécurité en cours (avec timeout prolongé)..."
        sh """
            mkdir -p ${REPORT_DIR}
            mkdir -p ${TRIVY_CACHE}

            # On augmente le timeout à 20 minutes et on cible explicitement le DB-Repository
            docker run --rm \
                -u \$(id -u):\$(id -g) \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v ${TRIVY_CACHE}:/root/.cache/trivy \
                -v ${REPORT_DIR}:/reports \
                aquasec/trivy:0.69.3 image \
                --timeout 20m \
                --db-repository public.ecr.aws/aquasecurity/trivy-db,ghcr.io/aquasecurity/trivy-db \
                --exit-code 0 \
                --severity CRITICAL,HIGH,MEDIUM,LOW \
                --scanners vuln \
                --format json \
                --output /reports/trivy-raw.json \
                ${IMAGE_NAME}:${IMAGE_TAG}

            # Le reste de tes commandes JQ...
        """
    }
}
            }
            post {
                always {
                    archiveArtifacts artifacts: "trivy-reports/*.csv", allowEmptyArchive: true
                }
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    sh "echo \"${HARBOR_PASS}\" | docker login ${HARBOR_URL} -u \"${HARBOR_USER}\" --password-stdin"
                }
            }
        }

        stage('Docker Tag & Push') {
            steps {
                sh """
                docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
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
        success { echo "✅ Image publiée : ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}" }
        failure { echo "❌ Pipeline échoué ! Vérifiez les logs." }
        always { cleanWs() }
    }
}
