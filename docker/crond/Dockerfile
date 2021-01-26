FROM frolvlad/alpine-python3

RUN apk update \
  && apk --no-cache add rsync \
  && python -m pip install --upgrade pip \
  && python -m pip install --no-cache-dir mcrcon

COPY crontab /var/spool/cron/crontabs/root
COPY daily.py /

CMD ["crond", "-f", "-d", "8"]
