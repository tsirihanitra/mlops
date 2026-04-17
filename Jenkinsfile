pipeline {
    agent any

    environment {
        // Configuration Harbor
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        
        // Configuration Trivy - CACHE PERSISTANT
        REPORT_DIR     = "${env.WORKSPACE}/trivy-reports"
        // On place le cache en dehors du workspace pour qu'il survive au cleanWs()
        TRIVY_CACHE    = "/var/lib/jenkins/trivy_shared_cache"
    }

    stages {
        stage('Initialisation') {
            steps {
                // S'assure que le dossier de cache existe sur l'hôte Jenkins
                sh "mkdir -p ${TRIVY_CACHE}"
                sh "mkdir -p ${REPORT_DIR}"
                
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
                echo "Lancement du scan de sécurité..."
                echo "Note : Le premier téléchargement peut être long (~1h), les suivants seront instantanés."
                
                sh """
                    # --timeout 90m : Large marge pour la connexion lente
                    # --db-repository : GitHub (ghcr.io) est souvent plus stable
                    docker run --rm \
                        -u \$(id -u):\$(id -g) \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \
                        -v ${REPORT_DIR}:/reports \
                        aquasec/trivy:0.69.3 image \
                        --timeout 90m \
                        --db-repository ghcr.io/aquasecurity/trivy-db,public.ecr.aws/aquasecurity/trivy-db \
                        --exit-code 0 \
                        --severity CRITICAL,HIGH,MEDIUM,LOW \
                        --format json \
                        --output /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # Conversion du JSON en CSV pour l'archivage avec JQ
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["Package","ID","Severity","Installed","Fixed","Title"],(.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/rapport_vulnerabilites.csv
                """
            }
            post {
                always {
                    // Les rapports CSV apparaissent dans l'interface Jenkins (Build -> Artifacts)
                    archiveArtifacts artifacts: "trivy-reports/*.csv", allowEmptyArchive: true
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

        stage('Nettoyage Local') {
            steps {
                sh """
                    docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                """
            }
        }
    }

    post {
        success {
            echo "✅ Succès : Image analysée et poussée sur Harbor."
        }
        failure {
            echo "❌ Échec : Vérifiez les logs du scan ou de la connexion Harbor."
        }
        always {
            cleanWs()
        }
    }
}
