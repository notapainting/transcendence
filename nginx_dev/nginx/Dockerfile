FROM nginx:1.18.0

# update and install utilies
# RUN apt update -y && apt upgrade -y

# copy nginx's configuration file and self signed certificate for https
COPY ./conf/nginx-selfsigned.crt /etc/nginx/ssl/nginx-selfsigned.crt
COPY ./conf/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.key

COPY ./conf/default.conf /etc/nginx/conf.d/default.conf

# copy our websitemake 
COPY ./front /var/www/trmdr.com

# install WAF: ModSecurity
# RUN apt-get install -y m4 automake git g++
# RUN apt-get install -y bison build-essential ca-certificates curl dh-autoreconf doxygen
# RUN apt-get install -y flex gawk git iputils-ping libcurl4-gnutls-dev libexpat1-dev libgeoip-dev liblmdb-dev
# RUN apt-get install -y libpcre3-dev libpcre++-dev libssl-dev libtool libxml2 libxml2-dev libyajl-dev locales
# RUN apt-get install -y lua5.3-dev pkg-config wget zlib1g-dev zlibc libxslt1-dev libgd-dev

# RUN cd /opt && git clone https://github.com/SpiderLabs/ModSecurity 
# RUN cd ModSecurity

# RUN git submodule init
# RUN git submodule update

# RUN ./build.sh 
# RUN ./configure && make && make install

# RUN cd /opt && git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

# RUN cd /opt && sudo wget http://nginx.org/download/nginx-1.18.0.tar.gz && tar -xvzmf nginx-1.18.0.tar.gz && rm -rf nginx-1.18.0.tar.gz

# RUN cd nginx-1.18.0

# RUN echo "./configure --add-dynamic-module=../ModSecurity-nginx" > tmp1 && nginx -V &> tmp2 && awk -F'arguments:' '{print $2}' tmp2 | tail -n 1 >> tmp1 && tr -d "\n\r" < tmp1 > cmd

# RUN bash cmd && rm tmp1 tmp2 cmd && make modules

# RUN mkdir /etc/nginx/modules && cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules && rm -rf /usr/share/modsecurity-crs

# RUN git clone https://github.com/coreruleset/coreruleset /usr/local/modsecurity-crs

# RUN mv /usr/local/modsecurity-crs/crs-setup.conf.example /usr/local/modsecurity-crs/crs-setup.conf && mv /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf

# RUN mkdir -p /etc/nginx/modsec && cp /opt/ModSecurity/unicode.mapping /etc/nginx/modsec && cp /opt/ModSecurity/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf

# ## change the value of SecRuleEngine to On
# RUN sed -i '7s/.*/SecRuleEngine On/' /etc/nginx/modsec/modsecurity.conf

# RUN touch /etc/nginx/modsec/main.conf
# RUN echo "Include /etc/nginx/modsec/modsecurity.conf" > /etc/nginx/modsec/main.conf
# RUN echo "Include /usr/local/modsecurity-crs/crs-setup.conf" >> /etc/nginx/modsec/main.conf
# RUN echo "Include /usr/local/modsecurity-crs/rules/*.conf" >> /etc/nginx/modsec/main.conf
