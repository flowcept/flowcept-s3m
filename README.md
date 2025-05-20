# Flowcept S3M CLI

Command-line interface to manage Flowcept's streaming service and cluster configurations using a YAML-based settings file.

## 📦 Requirements

```bash
pip install -r requirements.txt
```

## Usage

First, get your API Token at: https://s3m-myolcf.apps.olivine.ccs.ornl.gov/s3m/new-token

All operations require a settings.yaml file that defines your clusters and their configuration. Pass it using the --settings flag.

Example:

```
python flowcept-s3m.py --settings path/to/settings.yaml --deploy_mq
```

## Commands

You must provide exactly one of the following options:

### --deploy_mq

Deploy the streaming message queue service using cluster specifications from the provided settings.yaml.

```bash
python flowcept-s3m.py --settings settings.yaml --deploy_mq
```

### --list_clusters
List all clusters defined in the settings file.


```bash
python flowcept-s3m.py --settings settings.yaml --list_clusters
```

### --get_cluster <cluster_name>

Display the configuration details for a specific cluster.

```bash
python flowcept-s3m.py --settings settings.yaml --get_cluster my-cluster
```



## S3M Docs

https://s3m.apps.olivine.ccs.ornl.gov/docs/rest/streaming.html