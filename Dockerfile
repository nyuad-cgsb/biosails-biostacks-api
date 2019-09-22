FROM continuumio/miniconda3:4.5.11

RUN apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y \
    vim-tiny vim-athena ssh openssh-server build-essential

# Because of file permissions issues, we need to actually run this as root

USER root
COPY environment.yml environment.yml

RUN conda env create -f environment.yml
RUN echo "alias l='ls -lah'" >> ~/.bashrc
RUN echo "source activate sequencer-automation" >> ~/.bashrc

RUN mkdir -p  /root/airflow
COPY airflow/airflow_cors.patch /root/airflow_cors.patch

ENV AIRFLOW_HOME /root/airflow
ENV C_FORCE_ROOT true
ENV CONDA_EXE /opt/conda/bin/conda
ENV CONDA_PREFIX /opt/conda/envs/sequencer-automation
ENV CONDA_PYTHON_EXE /opt/conda/bin/python
ENV CONDA_PROMPT_MODIFIER (sequencer-automation)
ENV CONDA_DEFAULT_ENV sequencer-automation
ENV PATH /opt/conda/envs/sequencer-automation/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
## This is niceness added for the sake of my IDE
ENV PYTHONPATH "/root/dags:${PYTHONPATH}"

RUN mv /root/airflow_cors.patch /opt/conda/envs/sequencer-automation/lib && \
    cd /opt/conda/envs/sequencer-automation/lib && \
    patch python3.6/site-packages/airflow/www/app.py airflow_cors.patch

# Airflow stopped included their tests in the distro
# Probably because certain tests need to be run against certain architectures
# But I NEED tests to understand things
# So here we are
RUN wget https://github.com/apache/airflow/archive/1.10.3post1.zip \
    && unzip 1.10.3post1.zip \
    && cd airflow-1.10.3post1 \
    && mv tests /opt/conda/envs/sequencer-automation/lib/python3.6/site-packages/airflow/ \
    && cd ../ && rm -rf airflow-1.10.3post1


