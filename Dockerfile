FROM tomkat/python-base:latest

ENV TZ=Europe/Kiev

COPY requirements.txt /app/
RUN pip install  --no-cache-dir -r requirements.txt

WORKDIR /app

COPY main.py /app/jsonserver.py
COPY db.py /app/fbextract.py
COPY templates /app/templates

CMD [ "python3", "jsonserver.py" ]
