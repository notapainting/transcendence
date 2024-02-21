server {

    listen 443 ssl;
    listen [::]:433;
    include snippets/self-signed.conf;
    include snippets/ssl-params.conf;

    root /var/www/trmdr.com;

    index index.html;
    server_name trmdr.com www.trmdr.com;

    location / {
        try_files $uri $uri/ =404;
    }
}

server {
    listen 80;
    listen [::]:80;

    server_name trmdr.com www.trmdr.com;

  return 301 https://$server_name$request_uri;
}