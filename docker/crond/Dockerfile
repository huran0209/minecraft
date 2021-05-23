FROM frolvlad/alpine-python3

RUN apk update \
  && apk --no-cache add rsync jq \
  && python -m pip install --upgrade pip \
  && python -m pip install --no-cache-dir mcrcon yq

COPY crontab /var/spool/cron/crontabs/root
COPY daily /
COPY weekly /

CMD ["crond", "-f", "-d", "8"]
# 	-f	Foreground
# 	-d N	Set log level (0 most verbose), log to stderr
