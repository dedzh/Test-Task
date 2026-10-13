FROM python:3.10-slim

RUN useradd -m sudden

WORKDIR /home/sudden

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY app app
COPY server.py config.py boot.sh posts.csv ./
RUN chmod +x boot.sh

ENV FLASK_APP=server.py
ENV ES_HOST=http://elastic:9200

RUN chown -R sudden:sudden ./
USER sudden

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]