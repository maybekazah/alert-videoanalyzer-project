FROM nginx:1.26.3

COPY nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /app

COPY . .

RUN chown -R nginx:nginx /app

CMD ["nginx", "-g", "daemon off;"]