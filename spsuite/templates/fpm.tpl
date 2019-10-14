;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; DO NOT EDIT THIS FILE.
;
; Your changes to this file will be overwritten by ServerPilot.
;
; For information on how to customize php settings, see
; https://serverpilot.io/community/articles/customize-php-settings.html
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

[{{ appname }}]

prefix = /srv/users/{{ username }}

user = {{ username }}
group = {{ username }}

listen = /srv/users/{{ username }}/run/$pool.php-fpm.sock
listen.owner = {{ username }}
listen.group = www-data
listen.mode = 660

env[PATH] = /opt/sp/php{{ php }}/bin:/sbin:/usr/sbin:/bin:/usr/bin
env[TMPDIR] = /srv/users/{{ username }}/tmp/$pool
env[TEMP] = /srv/users/{{ username }}/tmp/$pool
env[TMP] = /srv/users/{{ username }}/tmp/$pool

access.log = /srv/users/{{ username }}/log/$pool/$pool_php{{ php }}.access.log
access.format = "%{HTTP_X_FORWARDED_FOR}e - [%t] \"%m %r%Q%q\" %s %l - %P %p %{seconds}d %{bytes}M %{user}C%% %{system}C%% \"%{REQUEST_URI}e\""
slowlog = /srv/users/{{ username }}/log/$pool/$pool_php{{ php }}.slow.log
request_slowlog_timeout = 5s
catch_workers_output = yes

php_value[error_log] = /srv/users/{{ username }}/log/$pool/$pool_php{{ php }}.error.log
php_value[mail.log] = /srv/users/{{ username }}/log/$pool/$pool_php{{ php }}.mail.log
php_value[doc_root] = /srv/users/{{ username }}/apps/$pool/public
php_value[upload_tmp_dir] = /srv/users/{{ username }}/tmp/$pool
php_value[session.save_path] = /srv/users/{{ username }}/tmp/$pool

pm.status_path = /php-fpm-status
ping.path = /php-fpm-ping

include = /etc/php{{ php }}-sp/fpm-pools.d/{{ appname }}.d/*.conf