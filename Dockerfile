
FROM python:3.6-slim

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
   
    cmake \
  
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


ENV PYTHONUNBUFFERED True
# Copy local code to the container image.

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./


# Install production dependencies.

RUN pip install -r requirements.txt

CMD python main.py

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
