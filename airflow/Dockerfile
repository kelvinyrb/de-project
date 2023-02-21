FROM apache/airflow:2.3.3

ENV AIRFLOW_HOME=/opt/airflow

# This switches the user to the root user in the container. This is necessary to install packages using apt-get.
USER root

# This installs the vim text editor using apt-get. The -qq and -qqq flags suppress output from the apt-get command. Also install ps.
RUN apt-get update -qq && apt-get install vim -qqq && apt-get install -y procps

# This sets the default shell for subsequent RUN commands to /bin/bash, and specifies some options to set strict error handling and debugging.
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# INSTALL GCLOUD AND ADD TO PATH
ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"
RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

# INSTALL OPENJDK AND ADD TO PATH
ARG OPENJDK_SDK_VERSION=11.0.2
ENV OPENJDK_HOME=/home/openjdk-sdk
ENV PATH="${OPENJDK_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://download.java.net/java/GA/jdk11/9/GPL/openjdk-${OPENJDK_SDK_VERSION}_linux-x64_bin.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/openjdk-sdk.tar.gz" \
    && mkdir -p "${OPENJDK_HOME}" \
    && tar xzf "${TMP_DIR}/openjdk-sdk.tar.gz" -C "${OPENJDK_HOME}" --strip-components=1 \
    && rm -rf "${TMP_DIR}" \
    && java --version

# DOWNLOAD SPARK CONNECTORS FOR GCS AND BIGQUERY
ENV GCS_CONNECTOR_HOME=/home/spark-connectors/gcs-connector
RUN DOWNLOAD_URL="gs://hadoop-lib/gcs/gcs-connector-hadoop3-2.2.5.jar" \
    && mkdir -p "${GCS_CONNECTOR_HOME}" \
    && gsutil cp "${DOWNLOAD_URL}" "${GCS_CONNECTOR_HOME}"

ENV BIGQUERY_CONNECTOR_HOME=/home/spark-connectors/bigquery-connector
RUN DOWNLOAD_URL="gs://spark-lib/bigquery/spark-3.1-bigquery-0.28.0-preview.jar" \
    && mkdir -p "${BIGQUERY_CONNECTOR_HOME}" \
    && gsutil cp "${DOWNLOAD_URL}" "${BIGQUERY_CONNECTOR_HOME}"

# INSTALL SPARK AND ADD TO PATH
ARG SPARK_VERSION=3.3.1
ENV SPARK_HOME=/home/spark
ENV PATH="${SPARK_HOME}/bin/:${PATH}"
RUN DOWNLOAD_URL="https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/spark.tgz" \
    && mkdir -p "${SPARK_HOME}" \
    && tar xzf "${TMP_DIR}/spark.tgz" -C "${SPARK_HOME}" --strip-components=1 \
    && rm -rf "${TMP_DIR}" \
    && spark-submit --version

# Add python to PYTHONPATH
ENV PYTHONPATH="${SPARK_HOME}/python/:${PYTHONPATH}"
ENV PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.5-src.zip:${PYTHONPATH}"

# Switch user to AIRFLOW_USER
USER $AIRFLOW_UID

# This installs the Python packages listed in requirements.txt using pip. The --no-cache-dir flag prevents pip from using cached packages.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts scripts

WORKDIR $AIRFLOW_HOME
