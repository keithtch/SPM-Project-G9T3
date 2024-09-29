pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    # Create a virtual environment
                    python3 -m venv venv

                    # Activate the virtual environment
                    source venv/bin/activate

                    # Upgrade pip to the latest version
                    pip install --upgrade pip

                    # Install the required packages in the virtual environment
                    pip install coverage==7.6.1 Flask==3.0.0 Flask-Cors==4.0.0 PyMySQL==1.1.1 python-dotenv==1.0.1 requests==2.31.0
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    # Activate the virtual environment and run tests
                    source venv/bin/activate
                    coverage run -m unittest discover tests
                    coverage report
                '''
            }
        }
        stage('Build') {
            steps {
                echo "Building the application..."
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    # Activate the virtual environment and deploy your app
                    source venv/bin/activate
                    ssh -o StrictHostKeyChecking=no ec2-user@<your-ec2-instance-ip> << 'ENDSSH'
                        cd /path/to/your/app
                        git pull origin main
                        source venv/bin/activate
                        pip install -r requirements.txt
                        pm2 restart app
                    ENDSSH
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
