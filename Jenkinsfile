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

                    echo "📦 Initialisation workspace"
                    mkdir -p ${TRIVY_CACHE}
                    mkdir -p ${REPORT_DIR}

                    ls -lah ${WORKSPACE}
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

                    echo "🐍 Installation dépendances"
                    python3 -m pip install --break-system-packages -r requirements.txt

                    echo "🧪 Tests"
                    python3 tests/test_predict.py
                """
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    set -euxo pipefail

                    echo "🐳 Build Docker image"
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh """
                    set -euxo pipefail

                    echo "🔐 Lancement scan Trivy"

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
                        -o /reports/trivy-raw.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "📄 Vérification fichier Trivy"
                    ls -lah ${REPORT_DIR}
                    cat ${REPORT_DIR}/trivy-raw.json | head -n 20 || true
                """

                script {
                    // Conversion JSON → CSV (SANS jq docker → plus stable)
                    def jsonFile = readFile("${REPORT_DIR}/trivy-raw.json")

                    writeFile file: "${REPORT_DIR}/rapport_vulnerabilites.csv", text: """
Package,ID,Severity,Installed,Fixed,Title
"""

                    // Si JSON vide on skip proprement
                    if (jsonFile?.trim()) {
                        sh """
                            python3 - << 'EOF'
import json

file_path = "${REPORT_DIR}/trivy-raw.json"
out_path = "${REPORT_DIR}/rapport_vulnerabilites.csv"

with open(file_path) as f:
    data = json.load(f)

rows = []

if "Results" in data:
    for result in data["Results"]:
        if "Vulnerabilities" in result:
            for v in result["Vulnerabilities"]:
                rows.append([
                    v.get("PkgName",""),
                    v.get("VulnerabilityID",""),
                    v.get("Severity",""),
                    v.get("InstalledVersion",""),
                    v.get("FixedVersion",""),
                    (v.get("Title","") or "").replace(",", " ")
                ])

with open(out_path, "a") as f:
    for r in rows:
        f.write(",".join(r) + "\\n")

print("CSV generated:", len(rows), "vulnerabilities")
EOF
                        """
                    } else {
                        echo "⚠️ Aucun rapport Trivy généré"
                    }
                }
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

                        echo "🔑 Login Harbor"
                        echo "${P}" | docker login ${HARBOR_URL} -u "${U}" --password-stdin

                        echo "🏷️ Tag images"
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:latest

                        echo "🚀 Push images"
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
            echo "✅ Pipeline réussi : build + scan + push OK"
        }

        failure {
            echo "❌ Pipeline échoué : vérifier Trivy / Docker / Harbor logs"
        }

        always {
            cleanWs()
        }
    }
}
