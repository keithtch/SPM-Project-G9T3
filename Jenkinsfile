pipeline {
    agent any // Specify that the pipeline can run on any available Jenkins agent

    environment {
        // Define any environment variables needed for your application here
        FLASK_ENV = 'development' // or 'production', depending on your needs
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm // Check out the source code from the configured SCM (Git)
            }
        }
        stage('Install Dependencies') {
            steps {
                // Install Python dependencies using pip
                sh '''
                    # Check if pip is installed, if not, install it using get-pip.py
                    if ! command -v pip &> /dev/null; then
                        echo "pip not found, installing..."
                        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                        python3 get-pip.py --user
                    fi

                    # Install dependencies from requirements.txt
                    pip install --upgrade --user pip # Upgrade pip to the latest version
                    pip install --user coverage==7.6.1 Flask==3.0.0 Flask-Cors==4.0.0 PyMySQL==1.1.1 python-dotenv==1.0.1 requests==2.31.0
                '''
            }
        }
        stage('Run Tests') {
            steps {
                // Run your tests here; update the command based on your testing framework
                sh '''
                    # Assuming you have test files set up with coverage
                    coverage run -m unittest discover tests
                    coverage report
                '''
            }
        }
        stage('Build') {
            steps {
                // You can add build steps here if needed
                echo "Building the application..."
            }
        }
        stage('Deploy') {
            steps {
                // Deploy your application to the desired environment (e.g., EC2, Heroku)
                sh '''
                    # Deploying to an EC2 instance via SSH
                    ssh -o StrictHostKeyChecking=no ec2-user@<your-ec2-instance-ip> << 'ENDSSH'
                        cd /path/to/your/app
                        git pull origin main # Pull the latest code from the main branch
                        pip install -r requirements.txt # Install/update dependencies
                        # Assuming you're using a process manager like Gunicorn or PM2
                        pm2 restart app # Replace with your application's restart command
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
