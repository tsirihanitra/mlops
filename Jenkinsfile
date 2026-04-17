pipeline {
    agent any

    environment {
        // Harbor
        HARBOR_URL     = '192.168.43.53'
        HARBOR_PROJECT = 'mlops'
        IMAGE_NAME     = 'wine-quality'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"

        // Trivy
        REPORT_DIR     = "${env.WORKSPACE}/trivy-reports"
        TRIVY_CACHE    = "/var/lib/jenkins/trivy_shared_cache"
    }

    stages {

        stage('Initialisation') {
            steps {
                sh """
                    set -euxo pipefail

                    mkdir -p ${TRIVY_CACHE}
                    mkdir -p ${REPORT_DIR}

                    echo "📦 Clonage du repo..."
                """

                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/tsirihanitra/mlops.git'
            }
        }

        stage('Installation & Tests') {
            steps {
                sh """
                    set -euxo pipefail
                    python3 -m pip install --break-system-packages -r requirements.txt
                    python3 tests/test_predict.py
                """
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    set -euxo pipefail
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh """
                    set -euxo pipefail

                    echo "🔐 Scan Trivy en cours..."

                    docker run --rm \
                        -u \$(id -u):\$(id -g) \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \
                        -v ${REPORT_DIR}:/reports \
                        aquasec/trivy:0.69.3 image \
                        --timeout 90m \
                        --db-repository ghcr.io/aquasecurity/trivy-db \
                        --exit-code 0 \
                        --severity CRITICAL,HIGH,MEDIUM,LOW \
                        --format json \
                        --output /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "📄 Vérification du fichier JSON..."
                    ls -lah ${REPORT_DIR}
                """

                // ✅ Conversion JSON -> CSV (FIXED jq)
                sh """
                    set -euxo pipefail

                    docker run --rm \
                        -v ${REPORT_DIR}:/reports \
                        imega/jq \
                        jq -r '
                        ["Package","ID","Severity","Installed","Fixed","Title"],
                        (.Results[]?.Vulnerabilities[]? |
                        [.PkgName,
                         .VulnerabilityID,
                         .Severity,
                         .InstalledVersion,
                         (.FixedVersion // ""),
                         (.Title // "" | gsub(","; " "))])
                        | @csv' \
                        /reports/trivy-raw.json > ${REPORT_DIR}/rapport_vulnerabilites.csv
                """
            }

            post {
                always {
                    archiveArtifacts artifacts: "trivy-reports/*.csv", allowEmptyArchive: true
                }
            }
        }

        stage('Docker Login & Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'harbor-credentials',
                    usernameVariable: 'U',
                    passwordVariable: 'P'
                )]) {
                    sh """
                        set -euxo pipefail

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
            echo "✅ Succès : image build + scan + push Harbor OK"
        }
        failure {
            echo "❌ Échec pipeline : voir logs Trivy / Docker / Harbor"
        }
        always {
            cleanWs()
        }
    }
}
