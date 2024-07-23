pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        FLASK_APP_PATH = 'workspace/flask/app.py'  // Correct path to the Flask app
        PATH = "$VENV_PATH/bin:$PATH"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
		//SONARQUBE_TOKEN = ''
        DEPENDENCY_CHECK_HOME = '/var/jenkins_home/tools/org.jenkinsci.plugins.DependencyCheck.tools.DependencyCheckInstallation/OWASP_Dependency-Check/dependency-check'
    }
    
    stages {
        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }
        
        stage('Clone Repository') {
            steps {
                dir('workspace') {
                    git branch: 'main', url: 'https://github.com/vroomtest/Practical_Test'
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                dir('workspace/flask') {
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }
        
        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        set +e
                        source $VENV_PATH/bin/activate
                        pip install -r requirements.txt
                        set -e
                    '''
                }
            }
        }
        
		stage('Integration Testing') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        set +e
                        source $VENV_PATH/bin/activate
                        pytest --junitxml=integration-test-results.xml
                        set -e
                    '''
                }
            }
        }
		
        stage('Dependency Check') {
            steps {
                withCredentials([string(credentialsId: 'NVD_API_KEY', variable: 'NVD_API_KEY')]) {
                    script {
                        sh 'mkdir -p workspace/flask/dependency-check-report'
                        sh 'echo "Dependency Check Home: ${DEPENDENCY_CHECK_HOME}"'
                        sh 'ls -l ${DEPENDENCY_CHECK_HOME}/bin'
                        sh '''
                        //${DEPENDENCY_CHECK_HOME}/bin/dependency-check.sh --project "Flask App" --scan . --format "ALL" --out workspace/flask/dependency-check-report --cveValidForHours 12 --nvdApiKey ${NVD_API_KEY} || true
						${DEPENDENCY_CHECK_HOME}/bin/dependency-check.sh --project "Flask App" --scan . --format "ALL" --out workspace/flask/dependency-check-report --nvdApiKey ${NVD_API_KEY} || true
                        '''
                    }
                }
            }
        }
        
        stage('UI Testing') {
            steps {
                dir('workspace/flask') {
                    script {
                        sh '''
                            set +e
                            source $VENV_PATH/bin/activate
                            FLASK_APP=$FLASK_APP_PATH flask run &
                            sleep 5
                            curl -s http://127.0.0.1:5000 || echo "Flask app did not start"
                            curl -s -X POST -F "password=5TrongP@ssw0rd" http://127.0.0.1:5000 | grep "Welcome"
                            curl -s -X POST -F "password=password" http://127.0.0.1:5000 | grep "Password does not meet the requirements"
                            pkill -f "flask run"
                            set -e
                        '''
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir('workspace/flask') {
                    sh 'docker build -t flask-app .'
                }
            }
        }
        
		stage('SonarQube Analysis') {
			steps {
				withSonarQubeEnv('SonarQube') {
					withCredentials([string(credentialsId: 'SONARQUBE_KEY', variable: 'SONARQUBE_TOKEN')]) {
						dir('workspace/flask') {
							sh '''
							${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \
							-Dsonar.projectKey=flask-app \
							-Dsonar.sources=. \
							-Dsonar.inclusions=app.py \
							-Dsonar.host.url=http://sonarqube:9000 \
							-Dsonar.login=${SONARQUBE_TOKEN}
							'''
						}
					}
				}
			}
		}
        
        stage('Deploy Flask App') {
            steps {
                script {
                    echo 'Deploying Flask App...'
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop'
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm'
                    sh 'docker run -d -p 5000:5000 flask-app'
                    sh 'sleep 10'
                }
            }
        }
    }
    
    post {
        failure {
            script {
                echo 'Build failed, not deploying Flask app.'
            }
        }
        always {
            archiveArtifacts artifacts: 'workspace/flask/dependency-check-report/*.*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'workspace/flask/integration-test-results.xml', allowEmptyArchive: true
        }
    }
}
