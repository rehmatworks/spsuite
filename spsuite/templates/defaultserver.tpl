server {
    listen    80 default_server;
    listen    [::]:80 default_server;
    return    444;
}
server {
    listen    443 ssl default_server;
    listen    [::]:443 ssl default_server;
    ssl_certificate_key    ssl/_default.key;
    ssl_certificate        ssl/_default.crt;
    return    444;
}
