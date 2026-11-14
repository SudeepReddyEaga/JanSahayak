# ==============================================================================
# Dockerfile for Frontend UI Microservice (Port 3000 via Nginx)
# Serves the static interactive SPA and proxies /api/* calls to api-gateway:8000
# ==============================================================================
FROM nginx:1.27-alpine

# Copy custom Nginx reverse-proxy configuration
COPY services/frontend_ui/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static interactive frontend files
COPY services/frontend_ui/static /usr/share/nginx/html

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]

