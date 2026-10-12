pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        DOCKER_IMAGE_NAME = 'student-academic-platform'
        IMAGE_TAG = "v1.0.0"
    }

    stages {
        stage('SCM Checkout') {
            steps {
                echo 'Checking out source code from GitHub repository...'
                checkout scm
            }
        }

        stage('Environment Setup & Dependencies') {
            steps {
                echo 'Setting up Python 3.11 virtual environment and installing packages...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Code Linting & Syntax Gate') {
            steps {
                echo 'Executing static syntax and style checks via Flake8...'
                sh '''
                    . venv/bin/activate
                    flake8 app/ database/ --count --select=E9,F63,F7,F82 --show-source --statistics
                    flake8 app/ database/ tests/ --max-line-length=120 --statistics
                '''
            }
        }

        stage('Automated Unit & Integration Tests') {
            steps {
                echo 'Running Pytest test suites and exporting JUnit XML reports...'
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
                '''
            }
        }

        stage('Build Docker Artifact') {
            steps {
                echo "Packaging container image: ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}..."
                sh '''
                    docker build -t ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_IMAGE_NAME}:latest
                '''
            }
        }

        stage('Kubernetes Minikube Deployment') {
            steps {
                echo 'Applying Kubernetes manifests to Minikube cluster...'
                sh '''
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/student-deployment --timeout=60s
                '''
            }
        }
    }

    post {
        always {
            echo 'Archiving test execution reports...'
            junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
            cleanWs deleteDirs: true, notFailBuild: true
        }
        success {
            echo "CI/CD Pipeline executed successfully for build #${BUILD_NUMBER}!"
        }
        failure {
            echo "Build #${BUILD_NUMBER} FAILED! Inspect console log output for root cause."
        }
    }
}
