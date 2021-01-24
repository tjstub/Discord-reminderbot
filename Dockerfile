
FROM python:3.8.7-slim

RUN mkdir reminderbot
WORKDIR reminderbot
COPY main.py requirements.txt ./
COPY cogs/ ./cogs
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]