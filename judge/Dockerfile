FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ make libcap-dev pkg-config ca-certificates git \
    && git clone --depth 1 https://github.com/ioi/isolate.git /tmp/isolate \
    && make -C /tmp/isolate isolate install \
    && rm -rf /tmp/isolate /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./

ENTRYPOINT ["python", "run_judge.py"]
