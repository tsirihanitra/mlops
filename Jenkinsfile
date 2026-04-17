pipeline {
    agent any

    environment {
        // Configuration Harbor
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        
        // Configuration Trivy
        // On utilise des chemins relatifs au workspace pour la clarté Jenkins
        REPORT_DIR     = "trivy-reports"
        // Le cache est externe pour ne pas être effacé par cleanWs()
        TRIVY_CACHE    = "/var/lib/jenkins/trivy_shared_cache"
    }

    stages {
        stage('Initialisation') {
            steps {
                sh "mkdir -p ${REPORT_DIR}"
                sh "mkdir -p ${TRIVY_CACHE}"
                
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/tsirihanitra/mlops.git'
            }
        }

        stage('Installation & Tests') {
            steps {
                sh 'python3 -m pip install --break-system-packages -r requirements.txt'
                sh 'python3 tests/test_predict.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }



        stage('Docker Login & Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'U', passwordVariable: 'P')]) {
                    sh """
                        echo "${P}" | docker login ${HARBOR_URL} -u "${U}" --password-stdin
                        
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                        
                        docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline terminé avec succès. Image poussée sur Harbor."
        }
        failure {
            echo "❌ Le pipeline a échoué. Vérifiez les logs ci-dessus."
        }
        always {
            // Nettoyage du workspace (mais garde le TRIVY_CACHE car il est hors workspace)
            cleanWs()
        }
    }
}
