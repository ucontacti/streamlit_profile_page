# app/Dockerfile

FROM python:3.9.13

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

COPY . .

# RUN /usr/local/bin/python -m pip install --upgrade pip

RUN apt-get update && apt-get install -y libgdal-dev gdal-bin

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal

RUN export C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader omw-1.4
RUN python -m nltk.downloader stopwords

# ENTRYPOINT ["streamlit", "run", "1_🏠_Homepage.py", "--server.port=8501", "--server.address=0.0.0.0"]d