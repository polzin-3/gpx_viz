FROM python:3.7

COPY requirements.txt /tmp/
COPY ./app app/
WORKDIR "/app"

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

EXPOSE 8050

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]