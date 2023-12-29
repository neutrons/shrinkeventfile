FROM debian:buster-slim

# Dependencies
RUN apt update \
    && apt install -y \
      pkg-config \
      libhdf5-dev \
      python3-numpy \
      python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY ./ /app
RUN pip3 install .

CMD ["shrinkeventfile"]
