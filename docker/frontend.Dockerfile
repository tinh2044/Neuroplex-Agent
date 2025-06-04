FROM node:latest AS development
WORKDIR /app

COPY ./frontend/package*.json ./

RUN npm install --verbose --force

COPY ./frontend .

EXPOSE 5173

FROM node:latest AS build-stage
WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install --force

COPY ./frontend .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]