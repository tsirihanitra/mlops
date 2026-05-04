pipeline {
    agent any

    environment {
        HARBOR_URL     = 'docker.io'
        HARBOR_PROJECT = 'mirahasina'
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

        stage('Test') {
            steps {
                sh """
                    docker run --rm \\
                        -v \$(pwd):/app \\
                        -w /app \\
                        python:3.10-slim \\
                        bash -c "pip install -q -r requirements.txt && python tests/test_predict.py"
                """
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build -t ${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} \\
                               ${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                echo "Scan securite..."
                sh """
                    mkdir -p ${REPORT_DIR}
                    mkdir -p ${TRIVY_CACHE}

                    docker run --rm \\
                        -v /var/run/docker.sock:/var/run/docker.sock \\
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \\
                        -v \$(pwd)/${REPORT_DIR}:/reports \\
                        aquasec/trivy:0.69.3 image \\
                        --exit-code 0 \\
                        --severity CRITICAL,HIGH,MEDIUM,LOW \\
                        --scanners vuln \\
                        --format json \\
                        --output /reports/trivy-raw.json \\
                        --timeout 30m \\
                        ${HARBOR_PROJECT}/${IMAGE_NAME}:latest

                    docker run --rm \\
                        -v \$(pwd)/${REPORT_DIR}:/reports \\
                        imega/jq -r \\
                        '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \\
                        /reports/trivy-raw.json > ${REPORT_DIR}/resultat.csv

                    docker run --rm \\
                        -v \$(pwd)/${REPORT_DIR}:/reports \\
                        imega/jq -r \\
                        '["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],(.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))]) | @csv' \\
                        /reports/trivy-raw.json > ${REPORT_DIR}/resultat_critical.csv

                    echo "=== Resume du scan Trivy ==="
                    echo "CRITICAL : \$(tail -n +2 ${REPORT_DIR}/resultat_critical.csv | wc -l)"
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-reports/*.csv',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'harbor-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo \$DOCKER_PASS | docker login ${HARBOR_URL} -u \$DOCKER_USER --password-stdin
                        docker push ${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${HARBOR_PROJECT}/${IMAGE_NAME}:latest
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
                    docker pull ${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                    docker run -d \\
                        --name wine-prediction-app \\
                        -p 5000:5000 \\
                        --restart always \\
                        ${HARBOR_PROJECT}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Clean up') {
            steps {
                sh """
                    docker rmi ${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} || true
                """
            }
        }
    }

    post {
        success {
            echo "Deploiement reussi : http://localhost:5000"
        }
        failure {
            echo "Pipeline echoue ! Verifiez les logs."
        }
        always {
            cleanWs()
        }
    }
}
