pipeline {
    agent any

    environment {
        // Configuration Harbor
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        
        // Configuration Trivy
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
                // Installation des libs Python pour les tests locaux
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
                echo "Analyse de sécurité en cours..."
                sh """
                    mkdir -p ${REPORT_DIR}
                    mkdir -p ${TRIVY_CACHE}

                    # Scan principal : Génération du JSON (Timeout 20m pour éviter les erreurs réseau)
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
                        --format json \
                        --output /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # Extraction JQ : Création des rapports CSV par sévérité
                    
                    # Rapport Global
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["Package","ID","Severity","Installed","Fixed","Title"],(.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat.csv
                    
                    # Filtre CRITICAL
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["Package","ID","Severity","Installed","Fixed","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_critical.csv
                    
                    # Filtre HIGH
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["Package","ID","Severity","Installed","Fixed","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_high.csv

                    echo "=== Résumé du scan Trivy ==="
                    echo "CRITICAL : \$(tail -n +2 ${REPORT_DIR}/resultat_critical.csv | wc -l)"
                    echo "HIGH     : \$(tail -n +2 ${REPORT_DIR}/resultat_high.csv | wc -l)"
                """
            }
            post {
                always {
                    // Archivage des rapports CSV pour consultation dans Jenkins
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
        success {
            echo "✅ Pipeline terminé avec succès ! Image poussée sur Harbor."
        }
        failure {
            echo "❌ Le pipeline a échoué. Vérifiez les logs de l'étape en rouge."
        }
        always {
            // Nettoyage de l'espace de travail pour libérer de la place
            cleanWs()
        }
    }
}
