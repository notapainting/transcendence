FROM nginx:1.25.4

# Update and install utilies
SHELL ["/bin/bash", "-c"]
RUN apt update -y && apt upgrade -y


# Installation of the WAF: ModSecurity
RUN apt-get install -y m4 automake git vim \
	bison build-essential ca-certificates curl dh-autoreconf doxygen \
	flex gawk git iputils-ping libcurl4-gnutls-dev libexpat1-dev libgeoip-dev liblmdb-dev \
	libpcre3-dev libssl-dev libtool libxml2 libxml2-dev libyajl-dev locales \
	lua5.3-dev pkg-config wget zlib1g-dev zlib1g libxslt1-dev libgd-dev

	## Download ModSecurity
RUN git clone https://github.com/SpiderLabs/ModSecurity /opt/ModSecurity

	## Update and build ModSecurity 
RUN	cd /opt/ModSecurity \
	&& git submodule init /opt/ModSecurity \
	&& git submodule update /opt/ModSecurity \
	&& ./build.sh \
	&& ./configure && make && make install

	## Download ModSecurity connector for Nginx
WORKDIR	/opt
RUN git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

	## Download the same Nginx version as the container for the ModSecurity's module compilation
		### Retrieve the Nginx information
RUN	nginx -v &> tmp

		### Retrieve the Nginx's version and store the file's name we have to download
RUN	echo "nginx-" > tmpNginx \
	&& awk -F'/' '{ print $2 }' tmp >> tmpNginx \
	&& echo ".tar.gz" >> tmpNginx \
	&& tr -d "\n\r" < tmpNginx > Nginx

		### Store the command in a file which will extract the downloaded Nginx
RUN	echo "tar -xvzmf " > tmptarNginx \
	&& cat tmpNginx >> tmptarNginx \
	&& tr -d "\n\r" < tmptarNginx > tarNginx

		### Store the command in a file which will download the same Nginx's version
RUN	echo "wget http://nginx.org/download/" > tmpgetNginx \
	&& cat Nginx >> tmpgetNginx \
	&& tr -d "\n\r" < tmpgetNginx > getNginx

		### Execute the commands for dowloading and extraction Nginx
RUN	bash getNginx \
	&& bash tarNginx 

		### Remove temporaries files
RUN	rm -rf $(cat < Nginx) \
	&& rm -rf tmpNginx tmpgetNginx tmptarNginx Nginx getNginx tarNginx tmp


# Installation of the ModSecurity's module for Nginx
WORKDIR	/opt/nginx-1.25.4

	## Retrieve Nginx configuration's arguments and add it to the ModSecurity-nginx's configuration
RUN	echo "./configure --add-dynamic-module=../ModSecurity-nginx" > tmp1 \
	&& nginx -V &> tmp2 \
	&& awk -F'arguments:' '{print $2}' tmp2 | tail -n 1 >> tmp1 \
	&& tr -d "\n\r" < tmp1 > cmd 

	## Build of the ModSecurity's module for Nginx
RUN	bash cmd \
	&& rm tmp1 tmp2 cmd \
 	&& make modules

	## Copy the newly created module in Nginx's folder
RUN cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules


# Update the security level
WORKDIR	/
	## Delete the default security's rules and download a strict one
RUN rm -rf /usr/share/modsecurity-crs \
	&& git clone https://github.com/coreruleset/coreruleset /usr/local/modsecurity-crs

	## Use the default security rules
RUN mv /usr/local/modsecurity-crs/crs-setup.conf.example /usr/local/modsecurity-crs/crs-setup.conf \
	&& mv /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf \
	&& mkdir -p /etc/nginx/modsec \
	&& cp /opt/ModSecurity/unicode.mapping /etc/nginx/modsec \
	&& cp /opt/ModSecurity/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf

	## Reinforce the SecRuleEngine
RUN sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/nginx/modsec/modsecurity.conf

	## Include ModSecurity's rules to Nginx
RUN echo "Include /etc/nginx/modsec/modsecurity.conf" > /etc/nginx/modsec/main.conf \
	&& echo "Include /usr/local/modsecurity-crs/crs-setup.conf" >> /etc/nginx/modsec/main.conf \
	&& echo "Include /usr/local/modsecurity-crs/rules/*.conf" >> /etc/nginx/modsec/main.conf


# Copy nginx's self signed certificate for https #TEMPORAIRE
COPY ./conf/nginx-selfsigned.crt /etc/nginx/ssl/nginx-selfsigned.crt
COPY ./conf/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.key


# Copy our websitemake #TEMPORAIRE
COPY ./front /var/www/trmdr.com


# Copy our homemade Nginx's configuration
COPY ./conf/default.conf /etc/nginx/conf.d/default.conf


# Ask Ngingx to load the ModSecurity's module while it configure itself
RUN cat /etc/nginx/nginx.conf > /etc/nginx/temp.conf \
	&& awk 'NR<=6' /etc/nginx/temp.conf > /etc/nginx/nginx.conf \
	&& echo "load_module /etc/nginx/modules/ngx_http_modsecurity_module.so;" >> /etc/nginx/nginx.conf \
	&& awk 'NR>7' /etc/nginx/temp.conf >> /etc/nginx/nginx.conf \
	&& rm /etc/nginx/temp.conf


# Reboot the Nginx's container in order to apply every changes
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]