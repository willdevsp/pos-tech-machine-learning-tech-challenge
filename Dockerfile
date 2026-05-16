FROM nginx:1.27-alpine

# Copy a static frontend into Nginx default public directory.
COPY frontend/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
