pipeline {
    agent any

    environment {
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        REPORT_DIR     = 'trivy-reports'
        TRIVY_CACHE    = '/tmp/trivy-cache'
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

      stage('Security Scan (Trivy)') {
    steps {
        echo "Scan securite..."
        sh '''
            mkdir -p ${REPORT_DIR}
            mkdir -p ${TRIVY_CACHE}

            docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v ${TRIVY_CACHE}:/root/.cache/trivy \
                -v ${REPORT_DIR}:/reports \
                aquasec/trivy:0.69.3 image \
                --exit-code 0 \
                --severity CRITICAL,HIGH,MEDIUM,LOW \
                --scanners vuln \
                --format json \
                --output /reports/trivy-raw.json \
                --timeout 30m \
                192.168.43.53/mlops/wine-quality:latest

            docker run --rm \
                -v ${REPORT_DIR}:/reports \
                imega/jq -r \
                '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \
                /reports/trivy-raw.json > ${REPORT_DIR}/resultat.csv

            docker run --rm \
                -v ${REPORT_DIR}:/reports \
                imega/jq -r \
                '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \
                /reports/trivy-raw.json > ${REPORT_DIR}/resultat_critical.csv

            docker run --rm \
                -v ${REPORT_DIR}:/reports \
                imega/jq -r \
                '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \
                /reports/trivy-raw.json > ${REPORT_DIR}/resultat_high.csv

            docker run --rm \
                -v ${REPORT_DIR}:/reports \
                imega/jq -r \
                '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \
                /reports/trivy-raw.json > ${REPORT_DIR}/resultat_medium.csv

            docker run --rm \
                -v ${REPORT_DIR}:/reports \
                imega/jq -r \
                '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "LOW") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \
                /reports/trivy-raw.json > ${REPORT_DIR}/resultat_low.csv

            echo "=== Resume du scan Trivy ==="
            echo "CRITICAL : $(tail -n +2 ${REPORT_DIR}/resultat_critical.csv | wc -l)"
            echo "HIGH     : $(tail -n +2 ${REPORT_DIR}/resultat_high.csv | wc -l)"
            echo "MEDIUM   : $(tail -n +2 ${REPORT_DIR}/resultat_medium.csv | wc -l)"
            echo "LOW      : $(tail -n +2 ${REPORT_DIR}/resultat_low.csv | wc -l)"
        '''
    }
    post {
        always {
            archiveArtifacts artifacts: 'trivy-reports/resultat.csv, trivy-reports/resultat_critical.csv, trivy-reports/resultat_high.csv, trivy-reports/resultat_medium.csv, trivy-reports/resultat_low.csv',
                             allowEmptyArchive: true
        }
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

        stage('Deploy') {
            steps {
                sh """
                    docker stop wine-prediction-app || true
                    docker rm   wine-prediction-app || true
                    docker pull ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                    docker run -d \
                        --name wine-prediction-app \
                        -p 5000:5000 \
                        --restart always \
                        ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Clean up') {
            steps {
                sh """
                    docker rmi ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                """
            }
        }
    }

    post {
        success {
            echo "Deploiement reussi : http://192.168.43.53:5000"
        }
        failure {
            echo "Pipeline echoue ! Verifiez les logs."
        }
        always {
            cleanWs()
        }
    }
}
