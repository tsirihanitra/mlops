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

        stage('Security Scan (Trivy)') {
            steps {
                echo "Lancement du scan de sécurité (Sortie: JSON + CSV)..."
                
                sh """
                    # 1. Exécution du scan avec l'option --output correcte
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \
                        -v ${WORKSPACE}/${REPORT_DIR}:/reports \
                        aquasec/trivy:0.69.3 image \
                        --timeout 90m \
                        --format json \
                        --output /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """

                script {
                    // Vérification de sécurité pour éviter le crash "NoSuchFileException"
                    if (!fileExists("${REPORT_DIR}/trivy-raw.json")) {
                        error "ERREUR : Le rapport Trivy n'a pas été généré dans ${REPORT_DIR}."
                    }
                }

                sh """
                    # 2. Transformation du JSON en CSV lisible via JQ
                    docker run --rm -v ${WORKSPACE}/${REPORT_DIR}:/reports imega/jq -r '
                        ["Package","ID","Severity","Installed","Fixed"],
                        (.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, .FixedVersion]) 
                        | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/vulnerabilites_final.csv
                """
            }
            post {
                always {
                    // Archive le CSV pour qu'il soit téléchargeable dans l'interface Jenkins
                    archiveArtifacts artifacts: "${REPORT_DIR}/*.csv", allowEmptyArchive: true
                }
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
