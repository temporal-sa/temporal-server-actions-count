import time
import requests
import argparse
from prometheus_client.parser import text_string_to_metric_families

def scrape_metrics(prometheus_url):
    """Fetches metrics from the Prometheus endpoint and returns parsed data."""
    response = requests.get(prometheus_url)
    response.raise_for_status()  # Raise an error if the request failed
    return list(text_string_to_metric_families(response.text))

def get_action_count(metrics_data, included_namespace, excluded_namespace="temporal_system"):
    """Extracts and returns the total 'action' count from the parsed metrics data."""
    total_actions = 0
    for family in metrics_data:
        if family.name == 'action':
            for sample in family.samples:
                namespace = sample.labels.get('namespace')

                # Apply namespace filter and exclude specified namespace
                if (namespace != excluded_namespace and 
                    (included_namespace == "" or namespace == included_namespace)):
                    total_actions += sample.value
    return total_actions

def print_readme():
    """Prints a README message when no argument is provided."""
    readme_message = """
    Usage: python temporal-server-actions-count.py --time-window-seconds <time_window_in_seconds> [OPTIONS]

    This script monitors Prometheus action metrics from a Temporal Server and calculates the average actions
    per second and the total number of actions over the specified time window.

    Arguments:
      --time-window-seconds: The time period in seconds over which the total actions will be 
                             calculated and reported.

    Optional:
      --prometheus-url: The Prometheus scrape URL. Default is 'http://localhost:63626/metrics'.
      --included-namespace: The namespace to filter for. Default is all namespaces (None).
      
    Example:
      python temporal-server-actions-count.py --time-window-seconds 120
      python temporal-server-actions-count.py --time-window-seconds 120 --prometheus-url http://localhost:9090/metrics --included-namespace default
    """
    print(readme_message)

def main(time_window, prometheus_url, included_namespace):
    print(f"Starting Prometheus action metric monitoring with a time window of {time_window} seconds...")
    print(f"Monitoring Prometheus endpoint: {prometheus_url}")
    if included_namespace:
        print(f"Sampling only from namespace: {included_namespace}")
    else:
        print("Sampling from all namespaces.")
    print(f"Please wait, the total number of actions will be reported after {time_window} seconds...")

    last_action_count = None
    total_action_delta = 0
    start_time = time.time()

    while True:
        try:
            # Scrape and parse the metrics data
            metrics_data = scrape_metrics(prometheus_url)

            # Get the current action count from the metrics data
            current_action_count = get_action_count(metrics_data, included_namespace)

            # Calculate the difference between the current and last action count
            if last_action_count is not None:
                action_delta = current_action_count - last_action_count
                total_action_delta += action_delta
                actions_per_second = action_delta / 1  # Calculating actions per second

                # Report the average actions per second every second
                print(f"Current average actions per second: {actions_per_second:.2f}")

            # Update the last action count
            last_action_count = current_action_count

            # Wait for 1 second before the next scrape
            time.sleep(1)

            # Check if the total time has reached the specified time window
            if time.time() - start_time >= time_window:
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Print the total number of actions after the time window
    print(f"Total actions in the last {time_window} seconds: {total_action_delta}")
    print("Monitoring completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Prometheus action metrics and calculate average actions per second and total actions over a given time window.")
    
    # Arguments
    parser.add_argument("--time-window-seconds", type=int, required=True, help="The time period in seconds to capture the action metrics.")
    parser.add_argument("--prometheus-url", type=str, default="http://localhost:63626/metrics", help="The Prometheus scrape URL (default: http://localhost:63626/metrics).")
    parser.add_argument("--included-namespace", type=str, default="", help="The namespace to filter for. If not provided, samples all namespaces.")
    
    args = parser.parse_args()

    if args.time_window_seconds:
        main(args.time_window_seconds, args.prometheus_url, args.included_namespace)
    else:
        print_readme()
