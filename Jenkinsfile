pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // This step checks out the code from the specified GitHub repository
                checkout scm  // Assumes you have already configured GitHub in Jenkins
            }
        }
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    
                    sudo apt install python3.12-venv

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
        stage('Run Web Application') {
            steps {
                sh '''
                    # Activate the virtual environment and run the Flask web server
                    source venv/bin/activate
                    export FLASK_APP=Application/application.py  # Replace with your main application file
                    export FLASK_ENV=development  # Optional: Set to development for debugging
                    flask run --host=0.0.0.0 --port=5000 &  # Run the server in the background
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    # Activate the virtual environment and run tests
                    source venv/bin/activate
                    coverage run -m unittest discover tests  # Assuming you have a tests directory
                    coverage report
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Web application started without errors.'
        }
        failure {
            echo 'Pipeline failed! There were errors running the web application or tests.'
        }
    }
}
