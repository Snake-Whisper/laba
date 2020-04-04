FROM node:buster
ENV NG_CLI_ANALYTICS=ci
RUN apt-get update && apt-get install nginx -y
RUN npm install -g @angular/cli
RUN mkdir /app
RUN mkdir /files
COPY nginx-config /etc/nginx/sites-enables
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
