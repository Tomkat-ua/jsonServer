FROM bitnami/python:3.9-debian-12

ENV TZ=Europe/Kiev

WORKDIR /app

COPY requirements.txt /app/
COPY main.py /app/jsonserver.py
COPY fbextract.py /app/fbextract.py

RUN apt-get update  
RUN apt-get install  libfbclient2 -y --no-install-recommends
RUN pip install -r requirements.txt

#ENTRYPOINT ["bash"]
CMD [ "python3", "jsonserver.py" ]


