FROM logstash:7.6.1

WORKDIR /opt/opendata

ENV CSV_OUTPUT_DIRECTORY=/opt/opendata/csv
ENV ES_HOST=elasticsearch:9200

COPY exports ./exports
COPY logstash/conf ./conf
COPY logstash/cron/crontab

RUN pip install --no-cache-dir -r exports/requirements.txt

RUN yum install cronie

