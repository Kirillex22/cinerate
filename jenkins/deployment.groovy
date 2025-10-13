pipeline {
    agent any

    environment {
        APP_NAME = "cinerate-api"
        CONFIG_FILE="./repo/backend/config.yaml"
        COMPOSE_FILE = "docker-compose.yml"
        REPO_URL = "your_git_repository_url.git"  // Замените на URL вашего репозитория
        BRANCH = "main"   // или master — проверь в GitLab
    }
    
    stages {
        
       stage('Clean workspace') {
            steps {
                echo "🧹 Очищаем рабочую директорию..."
                // Этот шаг безопасно удаляет все, что было в workspace
                cleanWs() 
            }
        }

        stage('Checkout') {
            steps {
                echo "📦 Клонируем проект из GitLab вручную..."
                sh '''
                rm -rf repo || true
                git clone ${REPO_URL} repo
                cd repo
                git checkout ${BRANCH} || true
                '''
            }
        }
        
        stage('Prepare backend') {
            steps {
                dir('repo/backend') {
                    echo "🔧 Делаем start.sh исполняемым..."
                    sh 'chmod +x drop_config_to_env.sh'
                }
            }
        }
       stage('Generate config') {
            steps {
                dir('repo/backend') {
                    echo "🧩 Создаём backend/config.yaml..."
                    sh '''
                    cat > config.yaml <<EOF
APP_NAME: cinerate
API_VERSION: 1
POSTGRES_SETTINGS:
  USERNAME: test
  PASSWORD: test
  DB_NAME: test
  SCHEMA: public
  HOST: db
  PORT: 5432
EXTERNAL_API_SETTINGS:
  API_BASE_URL: https://api.kinopoisk.dev/v1.4
  API_ACCESS_TOKEN: kinpoiskdevtoken
SECURITY_SETTINGS:
  SECRET_KEY: supersecretkey
  ACCESS_TOKEN_EXPIRE_MINUTES: 60
ADMIN_USER:
  login: admin
  password: admin
        EOF
         '''
                }
            }
        }

        stage('Source drop_config_to_env.sh') {
            steps {
                dir('repo/backend') {
                    echo "⚙️ Загружаем переменные окружения..."
                    sh '''
                    if [ -f "./drop_config_to_env.sh" ]; then
                        ./drop_config_to_env.sh
                        ls -l
                        cat .env
                        cp .env ../.env       # копируем в корень repo
                        rm .env
                    else
                        echo "⚠️ Файл drop_config_to_env.sh не найден, пропускаем."
                    fi
                    '''
                }
            }
        }
        
        stage('Build & Deploy') {
            steps {
                dir('repo') {
                    echo "🐳 Запускаем docker-compose..."
                    sh '''
                    docker-compose --env-file .env down || true
                    docker-compose --env-file .env build 
                    docker-compose --env-file .env up -d
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Сервис успешно развернут!"
            sh 'docker ps'
        }
        failure {
            echo "❌ Ошибка при развертывании!"
        }
    }
}
