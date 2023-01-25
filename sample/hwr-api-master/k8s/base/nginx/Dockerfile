FROM nginx:1.21.4

RUN apt-get update && apt-get install -y vim

# Configure Nginx
COPY nginx.conf /etc/nginx/nginx.conf

COPY wait-for-it.sh /wait-for-it.sh

# Copy Entrypoint Script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
