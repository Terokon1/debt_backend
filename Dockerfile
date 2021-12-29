FROM python:3.9-alpine as builder

WORKDIR /usr/src/debt_backend

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/debt_backend/wheels -r requirements.txt


FROM python:3.9-alpine

RUN mkdir -p /home/app

RUN addgroup -S app && adduser -S app -G app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

RUN apk update && apk add gcc musl-dev libpq
COPY --from=builder /usr/src/debt_backend/wheels /wheels
COPY --from=builder /usr/src/debt_backend/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

COPY . $APP_HOME

RUN find $APP_HOME -print0 | xargs -P 100 -0 chown --no-dereference app:app

USER app
RUN chmod +x  $APP_HOME/entrypoint.sh
RUN python manage.py collectstatic

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
