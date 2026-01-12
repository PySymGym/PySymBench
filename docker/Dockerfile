FROM --platform=linux/arm64 ubuntu:22.04


ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

WORKDIR /workspace

RUN apt update && \
    apt install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        gnupg \
        software-properties-common \
        build-essential \
        cmake \
        clang \
        maven \
        locales \
        lsb-release \
        apt-transport-https && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    apt update && \
    apt install -y \
        dotnet-sdk-7.0 \
        dotnet-sdk-8.0 \
        python3.11 \
        python3.11-venv \
        python3.11-distutils && \
    locale-gen en_US.UTF-8 && \
    apt clean && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1


RUN python3 -m venv /opt/venv


ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel && \
    pip install poetry==2.2.1

ENV POETRY_HTTP_TIMEOUT=600
ENV PIP_DEFAULT_TIMEOUT=600


RUN git clone --depth=1 https://github.com/PySymGym/PySymGym.git /tmp/PySymGym

WORKDIR /workspace/PySymGym

RUN cp /tmp/PySymGym/pyproject.toml . && \
    cp /tmp/PySymGym/poetry.lock .

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-interaction --no-ansi --no-root

WORKDIR /workspace

RUN rm -rf PySymGym && \
    git clone https://github.com/PySymGym/PySymGym.git && \
    cd PySymGym && git submodule update --init --recursive

WORKDIR /workspace/PySymGym


RUN poetry install --no-interaction --no-ansi

WORKDIR /workspace/PySymGym/GameServers/VSharp

ENV MSBUILDDISABLENODEREUSE=1

ENV DOTNET_CLI_HOME=/tmp

ENV HOST_ARM64=1

RUN apt install -y clang libc6-dev

ENV CFLAGS="-Dg_arm64_atomics_present=1"
ENV CXXFLAGS="-Dg_arm64_atomics_present=1"

RUN dotnet remove GameServers/VSharp/VSharp.Explorer/VSharp.Explorer.fsproj \
    package Microsoft.ML.OnnxRuntime.Gpu --no-restore || true \

RUN dotnet add GameServers/VSharp/VSharp.Explorer/VSharp.Explorer.fsproj \
    package Microsoft.ML.OnnxRuntime --version 1.20.0 --no-restore \

RUN dotnet publish VSharp.ML.GameServer.Runner/VSharp.ML.GameServer.Runner.fsproj \
    -c Release \
    -r linux-arm64 \
    --self-contained true

WORKDIR /workspace/PySymGym/maps/DotNet/Maps

RUN dotnet build Root -c Release -maxcpucount:1

WORKDIR /workspace/PySymGym

CMD ["bash"]
