import argparse
import json
import os
import yaml
import sys
import requests
import curlify


_SETTINGS_PATH = os.getenv("INTERSECT_S3M_SETTINGS", "settings.yaml")

SETTINGS = None
BASE_HEADER = None

def _format_duration(seconds: int) -> str:
    """
    Converts a duration in seconds to days (if >= 86400) or hours.

    Parameters
    ----------
    seconds : int
        The number of seconds to convert.

    Returns
    -------
    str
        A formatted string in days or hours.
    """
    if seconds >= 86400:
        days = seconds / 86400
        return f"{days:.2f} days"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def load_settings(path):
    global SETTINGS
    global BASE_HEADER
    if not os.path.exists(path):
        print(f"Error: settings file not found at {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path) as f:
            SETTINGS = yaml.safe_load(f)

        api_token = SETTINGS["token"]
        BASE_HEADER = {
            "Authorization": f"{api_token}",
            "Content-Type": "application/json"
        }
    except yaml.YAMLError as e:
        print(f"Error parsing settings file: {e}", file=sys.stderr)
        sys.exit(1)


def deploy_streaming_service() -> dict:
    print("Deploying streaming service...")
    cluster_name = SETTINGS["streaming_mq"]["cluster_name"]
    cluster_type = SETTINGS["streaming_mq"]["cluster_type"]
    provision_cluster_url = SETTINGS["streaming_mq"]["provision_cluster"].replace("${CLUSTER_TYPE}", cluster_type)
    provision_request = {
        "kind": "dragonfly-general",
        "name": cluster_name,
        "resourceOptions": SETTINGS["streaming_mq"]["cluster_resources"]
    }
    response = requests.post(provision_cluster_url, headers=BASE_HEADER, json=provision_request)
    print(f"This is the executed CURL:\n{curlify.to_curl(response.request)}\n\n")
    return response.json()


def extend() -> dict:
    print("Extending streaming service...")
    cluster_name = SETTINGS["streaming_mq"]["cluster_name"]
    cluster_type = SETTINGS["streaming_mq"]["cluster_type"]
    provision_cluster_url = SETTINGS["streaming_mq"]["provision_cluster"].replace("${CLUSTER_TYPE}", cluster_type)
    extend_cluster_url = provision_cluster_url.replace("provision_cluster", "extend")
    extend_cluster_url += f"/{cluster_name}"

    response = requests.post(extend_cluster_url, headers=BASE_HEADER)
    print(f"This is the executed CURL:\n{curlify.to_curl(response.request)}\n\n")
    return response.json()


def get_cluster(cluster_name: str = None) -> dict:
    cluster_type = SETTINGS["streaming_mq"]["cluster_type"]
    get_cluster_url = SETTINGS["streaming_mq"]["get_cluster"].replace("${CLUSTER_TYPE}", cluster_type)
    print(f"Getting cluster '{cluster_name}'...")
    response = requests.get(get_cluster_url.replace("${CLUSTER_NAME}", cluster_name), headers=BASE_HEADER)
    print(f"This is the executed CURL:\n{curlify.to_curl(response.request)}\n\n")
    return response.json()


def list_clusters() -> list:
    cluster_type = SETTINGS["streaming_mq"]["cluster_type"]
    list_clusters_url = SETTINGS["streaming_mq"]["list_clusters"].replace("${CLUSTER_TYPE}", cluster_type)
    print(f"Listing clusters...")
    response = requests.get(list_clusters_url, headers=BASE_HEADER)
    print(f"This is the executed CURL:\n{curlify.to_curl(response.request)}\n\n")
    json_resp = response.json()
    for cluster in json_resp["clusters"]:
        lifetime = cluster.get("lifetime")
        seconds = lifetime.get("secondsRemaining")
        duration = _format_duration(seconds)
        print(f"Cluster {cluster['name']} still has {duration} remaining.\n\n")

    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Manage Flowcept S3M operations. Cluster names and specs must be defined in the settings.yaml file."
    )

    parser.add_argument(
        "--settings",
        required=True,
        help="Path to settings.yaml (required)"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--deploy_mq",
        action="store_true",
        help="Deploy streaming service using cluster info from settings.yaml"
    )

    group.add_argument(
        "--list_clusters",
        action="store_true",
        help="List all clusters defined in settings.yaml"
    )

    group.add_argument(
        "--get_cluster",
        metavar="cluster_name",
        help="Show specs for a specific cluster defined in settings.yaml"
    )

    group.add_argument(
        "--extend",
        action="store_true",
        help="Extend the lifetime of the cluster defined in settings.yaml"
    )

    args = parser.parse_args()

    load_settings(args.settings)
    r = None
    if args.deploy_mq:
        r = deploy_streaming_service()
    elif args.list_clusters:
        r = list_clusters()
    elif args.get_cluster:
        r = get_cluster(args.get_cluster)
    elif args.extend:
        r = extend()
    print(r)


if __name__ == "__main__":
    main()


