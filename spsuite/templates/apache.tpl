<VirtualHost 127.0.0.1:81>
    Define DOCUMENT_ROOT /srv/users/{{ username }}/apps/{{ appname }}/public
    Define PHP_PROXY_URL unix:/srv/users/{{ username }}/run/{{ appname }}.php-fpm.sock|fcgi://localhost

    ServerAdmin webmaster@
    DocumentRoot ${DOCUMENT_ROOT}
    ServerName {{ servername }}{% if serveralias %}
    ServerAlias {{ serveralias }}{% endif %}

    ErrorLog "/srv/users/{{ username }}/log/{{ appname }}/{{ appname }}_apache.error.log"
    CustomLog "/srv/users/{{ username }}/log/{{ appname }}/{{ appname }}_apache.access.log" common

    RemoteIPHeader X-Real-IP
    SetEnvIf X-Forwarded-SSL on HTTPS=on
    SetEnvIf X-Forwarded-Proto https HTTPS=on

    SuexecUserGroup {{ username }} {{ username }}

    IncludeOptional /etc/apache-sp/vhosts.d/{{ appname }}.d/*.conf
</VirtualHost>
