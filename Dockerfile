FROM python:2.7

RUN mkdir /app
WORKDIR /app

ADD . /app

RUN pip install numpy
RUN pip install -r requirements.txt

CMD ["python", "iWorker.py"]
