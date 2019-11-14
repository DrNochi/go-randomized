FROM tensorflow/tensorflow:latest-gpu-py3

# Install node
RUN apt-get install -y nodejs

# Setup environment
ARG WORKDIR=/gobby
WORKDIR ${WORKDIR}
VOLUME ${WORKDIR}

ENV HOME=${WORKDIR}/.cache/container_home

# Setup python
COPY requirements.txt .
RUN pip install -r requirements.txt; rm requirements.txt
ENV PYTHONPATH=${WORKDIR}:${PYTHONPATH}

# Expose Flask default port
EXPOSE 5000
