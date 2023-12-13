### 1. Get Linux
FROM alpine:3.7

WORKDIR /code

### 2. Get Java via the package manager
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre

### 3. Get Python, PIP

RUN apk add --no-cache python \
&& python -m ensurepip \
&& pip install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python /usr/bin/python; fi && \
rm -r /root/.cache

COPY . .

### Get Flask for the app
RUN pip install -r requirements.txt

####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

#ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

####
EXPOSE 80

CMD ["python", "app.py"]