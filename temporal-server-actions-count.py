import time
import requests
import argparse
import logging
from prometheus_client.parser import text_string_to_metric_families
from typing import List, Optional

def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_metrics(prometheus_url: str) -> List:
    """Fetch metrics from the Prometheus endpoint and return parsed data."""
    try:
        response = requests.get(prometheus_url, timeout=10)
        response.raise_for_status()
        return list(text_string_to_metric_families(response.text))
    except requests.RequestException as e:
        logging.error(f"Failed to scrape metrics: {e}")
        return []

def get_action_count(metrics_data: List, included_namespace: Optional[str], excluded_namespace: str = "temporal_system") -> float:
    """Extract and return the total 'action' count from the parsed metrics data."""
    return sum(
        sample.value
        for family in metrics_data
        if family.name == 'action'
        for sample in family.samples
        if sample.labels.get('namespace') != excluded_namespace
        and (not included_namespace or sample.labels.get('namespace') == included_namespace)
    )

def print_readme() -> None:
    """Print a README message when no argument is provided."""
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

def monitor_actions(time_window: int, prometheus_url: str, included_namespace: Optional[str]) -> None:
    """Monitor action metrics and report results."""
    logging.info(f"Starting Prometheus action metric monitoring with a time window of {time_window} seconds...")
    logging.info(f"Monitoring Prometheus endpoint: {prometheus_url}")
    logging.info(f"Sampling from {'all namespaces' if not included_namespace else f'namespace: {included_namespace}'}")
    logging.info(f"Please wait, the total number of actions will be reported after {time_window} seconds...")

    last_action_count = None
    total_action_delta = 0
    start_time = time.time()

    try:
        while time.time() - start_time < time_window:
            metrics_data = scrape_metrics(prometheus_url)
            current_action_count = get_action_count(metrics_data, included_namespace)

            if last_action_count is not None:
                action_delta = current_action_count - last_action_count
                total_action_delta += action_delta
                actions_per_second = action_delta

                logging.info(f"Current average actions per second: {actions_per_second:.2f}")

            last_action_count = current_action_count
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Monitoring interrupted by user.")
    
    logging.info(f"Total actions in the last {time_window} seconds: {total_action_delta}")
    logging.info("Monitoring completed.")

def main() -> None:
    """Main function to parse arguments and start monitoring."""
    parser = argparse.ArgumentParser(description="Monitor Prometheus action metrics and calculate average actions per second and total actions over a given time window.")
    
    parser.add_argument("--time-window-seconds", type=int, required=True, help="The time period in seconds to capture the action metrics.")
    parser.add_argument("--prometheus-url", type=str, default="http://localhost:63626/metrics", help="The Prometheus scrape URL (default: http://localhost:63626/metrics).")
    parser.add_argument("--included-namespace", type=str, default=None, help="The namespace to filter for. If not provided, samples all namespaces.")
    
    args = parser.parse_args()

    setup_logging()
    
    if args.time_window_seconds:
        monitor_actions(args.time_window_seconds, args.prometheus_url, args.included_namespace)
    else:
        print_readme()

if __name__ == "__main__":
    main()