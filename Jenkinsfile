pipeline {
    agent any

    environment {
        DOCKERFILE_PATH = "./Dockerfile"
        DOCKER_IMAGE_NAME = ""
        TRIVY_REPORT_PATH ="trivy-scan-report.json"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/sahu04/node_js.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Set dockerImageName as an environment variable
                    DOCKER_IMAGE_NAME = sh(script: "awk 'NR==1 {print \$2}' ${DOCKERFILE_PATH}", returnStdout: true).trim()
                    sh "docker build -t ${DOCKER_IMAGE_NAME} -f ${DOCKERFILE_PATH} ."
                }
            }
        }

        stage('Vulnerability Scan - Docker Trivy') {
            steps {
                script {
                    echo "Running Trivy scan for image: ${DOCKER_IMAGE_NAME}"
                    sh "trivy --exit-code 1 --severity HIGH,MEDIUM,LOW --format json -o ${TRIVY_REPORT_PATH} ${DOCKER_IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            script {
                sh "docker rmi ${DOCKER_IMAGE_NAME}"
                archiveArtifacts artifacts: 'trivy-scan-report.json', followSymlinks: false
            }
        }
    }
}
