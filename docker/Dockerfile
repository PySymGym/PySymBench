FROM --platform=linux/amd64 ubuntu:24.04

WORKDIR /workspace

RUN apt update && \
    apt install -y \
        git \
        software-properties-common \
        ca-certificates \
        curl \
        gnupg && \
    add-apt-repository ppa:dotnet/backports && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y \
        build-essential \
        dotnet-sdk-7.0 \
        dotnet-sdk-9.0 \
        cmake \
        clang \
        maven \
        python3.11 \
        python3.11-venv \
        python3.11-distutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel --timeout 300 && \
    pip install poetry==2.2.1

RUN git clone https://github.com/PySymGym/PySymGym.git && \
    cd PySymGym && \
    git submodule update --init --recursive

WORKDIR /workspace/PySymGym

ENV POETRY_HTTP_TIMEOUT=300
ENV PIP_DEFAULT_TIMEOUT=300

RUN poetry install --no-interaction --no-ansi

WORKDIR /workspace/PySymGym/GameServers/VSharp
RUN dotnet build VSharp.ML.GameServer.Runner -c Release

WORKDIR /workspace/PySymGym/maps/DotNet/Maps
RUN dotnet build Root -c Release

WORKDIR /workspace/PySymGym

CMD ["bash"]
