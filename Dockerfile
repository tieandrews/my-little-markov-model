FROM python:3.10-bullseye

WORKDIR /code

COPY ./requirements.txt /code/my-little-markov-model/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/my-little-markov-model/requirements.txt

COPY ./src /code/my-little-markov-model/src

COPY ./models/markov-models/prod-models/ /code/my-little-markov-model/models/markov-models/prod-models

COPY ./main.py /code/my-little-markov-model/main.py

RUN ls --recursive /code/

EXPOSE $PORT

CMD python /code/my-little-markov-model/main.py
