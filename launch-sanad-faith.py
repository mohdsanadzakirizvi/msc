#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

sys.path.append(os.getcwd())

import yaml
import utils

from kubejobs.jobs import KubernetesJob


def argument_parser():
    parser = argparse.ArgumentParser(description="Backend Runner")
    parser.add_argument("config", type=str)
    parser.add_argument("--job-name", "-n", type=str, default="sanad-frontend")
    parser.add_argument("--gpu-type", type=str, default=None)
    parser.add_argument("--gpu-limit", type=int, default=None)
    parser.add_argument("--namespace", type=str, default="eidf097ns")
    args = parser.parse_args()
    return args


def main():
    args = argument_parser()
    configs = yaml.safe_load(open(args.config, "r"))

    job_name = args.job_name
    is_completed = utils.check_if_completed(job_name, namespace=args.namespace)

    if is_completed is True:
        # "sleep $((RANDOM % 300 + 300)) && " \
        base_args = "apt -y update && apt -y upgrade && " \
        "apt-get -y install git-lfs unzip psmisc wget git sudo python3 python-is-python3 pip bc htop nano nodejs npm curl && " \
        "git lfs install && " \
        "pip install -U pip && " \
        "git clone https://github.com/awesomealex1/faithful-reasoning.git && " \
        "cd faithful-reasoning && " \
        "pip install --root-user-action=ignore -U -r requirements.txt && " \
        "pip install --root-user-action=ignore -U protobuf && " \
        "pip install --root-user-action=ignore -U auto-gptq optimum autoawq && " \
        "wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.2-linux-x86_64.tar.gz -q && " \
        "tar -xzf elasticsearch-7.10.2-linux-x86_64.tar.gz && " \
        "useradd -m elasticsearchuser && " \
        "chown -R elasticsearchuser:elasticsearchuser elasticsearch-7.10.2 && " \
        "sudo -u elasticsearchuser elasticsearch-7.10.2/bin/elasticsearch && " \
        "sh scripts/download_react_data.sh && " \
        "uvicorn serve:app --port 8000 --app-dir src/utils/retriever_server && " \
        "python src/utils/retriever_server/build_index.py musique && " \
        "python src/utils/retriever_server/build_index.py hotpotqa && " \
        "python src/utils/retriever_server/build_index.py wikimultihopqa && " \
        "curl localhost:9200/_cat/indices && " \
        "python -m spacy download en_core_web_sm && " \
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python HF_TOKEN=$HF_TOKEN H4_TOKEN=$HF_TOKEN " \
        "HF_HUB_DISABLE_PROGRESS_BARS=1 CURL_CA_BUNDLE=\"\" "
        command = "&& sleep infinity "

        secret_env_vars = configs["env_vars"]

        # Create a Kubernetes Job with a name, container image, and command
        print(f"Creating job for: {command}")
        job = KubernetesJob(name=job_name, cpu_request="8", ram_request="80Gi",
                            image="nvcr.io/nvidia/cuda:12.0.0-cudnn8-devel-ubuntu22.04",
                            gpu_type="nvidia.com/gpu",
                            gpu_limit=configs["gpu_limit"] if args.gpu_limit is None else args.gpu_limit,
                            gpu_product=configs["gpu_product"] if args.gpu_type is None else args.gpu_type,
                            backoff_limit=1,
                            command=["/bin/bash", "-c", "--"],
                            args=[base_args + command],
                            secret_env_vars=secret_env_vars,
                            user_email="p.minervini@ed.ac.uk",
                            namespace=args.namespace,
                            kueue_queue_name=f"{args.namespace}-user-queue")

        # Run the Job on the Kubernetes cluster
        job.run()


if __name__ == "__main__":
    main()
