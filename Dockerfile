FROM ubuntu:bionic

ARG MANTID_FTP_SERVER="198.74.56.37"
ARG EVENT_FILE_MD5="34a9f4551d909093871a360d207e14ff"

# Dependencies
RUN apt update \
    && apt install -y \
        git \
        libhdf5-dev \
        python3-numpy \
        python3-pip \
        vim \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY ./requirements-dev.txt /app
RUN pip3 install -r requirements-dev.txt
COPY ./ /app

# Add test file
RUN wget -O /app/test_event_file.nxs http://${MANTID_FTP_SERVER}/ftp/external-data/MD5/${EVENT_FILE_MD5}

# Add my vimrc file
ARG VIMRC=""
RUN echo ${VIMRC}
RUN echo "${VIMRC}" >> /root/.vimrc

CMD ["python3", "./shrinkeventfile/shrinkeventfile.py"]
