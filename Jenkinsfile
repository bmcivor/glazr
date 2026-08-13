pipeline {
    agent any

    stages {
        stage('Backend tests') {
            steps {
                sh './scripts/test.sh backend'
            }
        }

        stage('Frontend tests') {
            steps {
                sh './scripts/test.sh frontend'
            }
        }

        stage('Backend quality checks') {
            steps {
                sh './scripts/lint.sh backend'
            }
        }

        stage('Frontend quality checks') {
            steps {
                sh './scripts/lint.sh frontend'
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v --remove-orphans || true'
        }
    }
}
