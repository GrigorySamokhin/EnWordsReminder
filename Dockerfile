FROM python:3.10

ENV C_FORCE_ROOT 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install system packages
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN apt update && apt install -y --no-install-recommends make git ca-certificates build-essential libssl-dev \
    zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev \
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python3-pip ffmpeg libsm6 libxext6 \
    python3-setuptools python3-dev libpng-dev pngquant
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip

COPY ./requirments.txt ./enwords/requirments.txt
RUN pip install -r ./enwords/requirments.txt

COPY ./ /enwords/

WORKDIR enwords
#EXPORT CURLOPT_SSLVERSION CURL_SSLVERSION_MAX_TLSv1_2
CMD ["python3", "bot.py"]
