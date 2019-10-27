#!/bin/sh
{{ certbotpath }} renew --non-interactive --config-dir /etc/nginx-sp/le-ssls --post-hook "service nginx-sp reload"
