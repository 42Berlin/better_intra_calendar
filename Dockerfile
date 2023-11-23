FROM python:3.10-bullseye

WORKDIR /app

COPY . /app/

RUN rm -rf /app/.git

RUN pip install pipenv 2>/dev/null
RUN pipenv install -r /app/requirements.txt 2>/dev/null

EXPOSE 4233

CMD ["pipenv", "run", "python", "/app/routes.py"]