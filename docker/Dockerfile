FROM ubuntu:24.04

WORKDIR /workspace

RUN apt update && \
    apt install -y git software-properties-common ca-certificates curl gnupg wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && \
    apt update && apt install -y dotnet-sdk-8.0

RUN add-apt-repository ppa:deadsnakes/ppa && apt update && \
    apt install -y build-essential cmake clang maven python3.11 python3.11-venv python3.11-distutils libz3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && pip install poetry==2.2.1

ENV POETRY_HTTP_TIMEOUT=600
ENV PIP_DEFAULT_TIMEOUT=600

RUN git clone --depth=1 https://github.com/PySymGym/PySymGym.git /tmp/PySymGym

WORKDIR /workspace/PySymGym

RUN cp /tmp/PySymGym/pyproject.toml . && cp /tmp/PySymGym/poetry.lock .

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-interaction --no-ansi --no-root

WORKDIR /workspace

RUN rm -rf PySymGym && git clone https://github.com/PySymGym/PySymGym.git && \
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

RUN sed -i \
  -e '/Microsoft.ML.OnnxRuntime.Gpu/d' \
  -e '/Microsoft.ML.OnnxRuntime.Linux.x64/d' \
  -e '/System.Numerics.Tensors/a\<PackageReference Include="Microsoft.ML.OnnxRuntime" Version="1.20.0" />' \
  VSharp.Explorer/VSharp.Explorer.fsproj

RUN dotnet build VSharp.ML.GameServer.Runner -c Release

WORKDIR /workspace/PySymGym/maps/DotNet/Maps
RUN dotnet build Root -c Release -maxcpucount:1

WORKDIR /workspace/PySymGym/tools/runstrat
ENTRYPOINT ["poetry", "run", "python3", "runstrat.py"]
