# Stage 1: Build stage
FROM nginx:alpine AS build

# Copy the nginx configuration to the main nginx configuration file
COPY deploy/nginx-docker/nginx.conf /etc/nginx/nginx.conf

# Add static content
COPY deploy/nginx-docker/index.html /usr/share/nginx/html/test/index.html

# Stage 2: Final stage
FROM nginx:alpine

COPY --from=build /etc/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /usr/share/nginx/html/test/index.html /usr/share/nginx/html/test/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
