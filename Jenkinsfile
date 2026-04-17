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
                echo "Analyse de sécurité en cours..."
                sh """
                    mkdir -p ${REPORT_DIR}
                    mkdir -p ${TRIVY_CACHE}

                    # 1. Génération du rapport JSON brut
                    docker run --rm \
                        -u \$(id -u):\$(id -g) \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \
                        -v ${REPORT_DIR}:/reports \
                        aquasec/trivy:0.69.3 image \
                        --exit-code 0 \
                        --severity CRITICAL,HIGH,MEDIUM,LOW \
                        --scanners vuln \
                        --format json \
                        --output /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # 2. Extraction JQ pour chaque niveau de sévérité
                    # Note : On utilise l'image jq pour transformer le JSON en CSV
                    
                    # Fonction utilitaire simplifiée pour JQ
                    JQUERY='["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv'

                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r "\$JQUERY" /reports/trivy-raw.json > ${REPORT_DIR}/resultat.csv
                    
                    # Filtres spécifiques par sévérité
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_critical.csv
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_high.csv
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_medium.csv
                    docker run --rm -v ${REPORT_DIR}:/reports imega/jq -r '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "LOW") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' /reports/trivy-raw.json > ${REPORT_DIR}/resultat_low.csv

                    echo "=== Résumé du scan Trivy ==="
                    echo "CRITICAL : \$(tail -n +2 ${REPORT_DIR}/resultat_critical.csv | wc -l)"
                    echo "HIGH     : \$(tail -n +2 ${REPORT_DIR}/resultat_high.csv | wc -l)"
                    echo "MEDIUM   : \$(tail -n +2 ${REPORT_DIR}/resultat_medium.csv | wc -l)"
                    echo "LOW      : \$(tail -n +2 ${REPORT_DIR}/resultat_low.csv | wc -l)"
                """
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
