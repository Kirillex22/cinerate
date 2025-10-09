# --- ЭТАП 1: Сборка Angular приложения ---
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Убедитесь, что в angular.json путь сборки правильный
# outputPath: "dist/cinerate-frontend/browser"
RUN npm run build -- --configuration production

# --- ЭТАП 2: Подготовка Nginx ---
# Используем официальный стабильный образ Nginx
FROM nginx:stable-alpine

# Копируем собранные файлы фронтенда из этапа 'build'
COPY --from=build /app/dist/cinerate-frontend /usr/share/nginx/html

# Копируем наш кастомный конфиг Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]