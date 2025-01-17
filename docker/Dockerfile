FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# setup timezone
RUN echo 'Etc/UTC' > /etc/timezone && \
    ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    apt-get update && \
    apt-get install -q -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .
# Copy requirements.txt into the container
COPY ./src/orison_ai/gateway_function/requirements.txt .
COPY ./docker/packages-apt.txt .
COPY ./docker/python_addons.txt .

# Install Python 3.11.14 and pip
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils && \
    apt-get install -y wget && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.11 get-pip.py && \
    rm get-pip.py
RUN echo "alias python=python3.11" >> /root/.bashrc
RUN echo "alias python3=python3.11" >> /root/.bashrc
RUN rm /usr/bin/python3
RUN ln -s /usr/bin/python3.11 /usr/bin/python3
# Install any additional Python packages needed
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt 
RUN python3.11 -m pip install --no-cache-dir -r python_addons.txt

# Install any additional system packages needed
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && xargs -a packages-apt.txt apt-get install -y

RUN chmod 755 /app/docker/entrypoint.sh

EXPOSE 5004
EXPOSE 5005

RUN echo 'export PYTHONPATH="${PYTHONPATH}:/app/src/"' >> /root/.bashrc

ENTRYPOINT ["bash",  "/app/docker/entrypoint.sh" ]