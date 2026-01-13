FROM ubuntu:24.04


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


RUN apt update && apt install -y libz3-dev

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
    package Microsoft.ML.OnnxRuntime --version 1.20.0 --no-restore

RUN dotnet build VSharp.ML.GameServer.Runner -c Release

WORKDIR /workspace/PySymGym/maps/DotNet/Maps

RUN dotnet build Root -c Release -maxcpucount:1

WORKDIR /workspace/

#TODO: extract these commands into a test script
WORKDIR /workspace/PySymGym/tools/runstrat

RUN mkdir -p artifacts

WORKDIR /workspace/PySymGym/tools/runstrat/resources

RUN dotnet build ForTests -c Release

WORKDIR /workspace/PySymGym/tools/runstrat
RUN poetry run pytest tests -sv  \
    -o log_file="artifacts/runstrat.log" \
    -o log_file_level="DEBUG"

CMD ["bash"]
