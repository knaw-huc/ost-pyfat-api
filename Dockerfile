FROM python:3.12.8-bookworm
LABEL authors="Menzo Windhouwer" 
#based on work by Eko Indarto on https://github.com/knaw-huc/ost-clarin-skg

ARG BUILD_DATE
ENV BUILD_DATE=$BUILD_DATE


# Combine apt-get commands to reduce layers
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash huc

ENV PYTHONPATH=/home/huc/ocs/src
ENV BASE_DIR=/home/huc/ocs

WORKDIR ${BASE_DIR}


# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.


# Create and activate virtual environment
RUN python -m venv .venv
ENV APP_NAME="ost-pyfat-api"
ENV PATH="/home/huc/ocs/.venv/bin:$PATH"
# Copy the application into the container.
COPY src ./src
#Temporary, will be removed later
COPY conf ./conf
COPY pyproject.toml .
COPY README.md .
COPY uv.lock .


RUN uv venv .venv
# Install dependencies

#RUN uv sync --frozen --no-cache
RUN uv sync --no-cache
RUN chown -R huc:huc ${BASE_DIR}
USER huc
RUN mkdir logs
# Run the application.
CMD ["python", "-m", "src.ost_pyfat_api.main"]

EXPOSE 41012

#CMD ["tail", "-f", "/dev/null"]