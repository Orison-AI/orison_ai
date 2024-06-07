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
COPY ./docker/packages-python3.txt .
COPY ./docker/packages-apt.txt .

# Install Python 3.9 and pip
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils && \
    apt-get install -y wget && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py
RUN echo "alias python=python3.10" >> /root/.bashrc
RUN echo "alias python3=python3.10" >> /root/.bashrc
RUN rm /usr/bin/python3
RUN ln -s /usr/bin/python3.10 /usr/bin/python3
# Install any additional Python packages needed
RUN python3.10 -m pip install --no-cache-dir -r packages-python3.txt

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
EXPOSE 3000

RUN echo 'export PYTHONPATH="${PYTHONPATH}:/app/src/"' >> /root/.bashrc

ENTRYPOINT ["bash",  "/app/docker/entrypoint.sh" ]