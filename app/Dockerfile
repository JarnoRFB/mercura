FROM alpine:3.7

RUN apk add --no-cache postgresql-dev gcc python3 python3-dev musl-dev gfortran build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

ADD requirements.txt /home/app/
WORKDIR /home/app/
RUN python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install -r requirements.txt

WORKDIR /
ADD ./ /home/app/
WORKDIR /home/app/

EXPOSE 5000

ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
