# Temporal Server Actions Count

This script monitors Prometheus action metrics from a Temporal Server and calculates the average actions per second and the total number of actions over the specified time window.

## Pre-requisites

Ensure you have Temporal workflows to run, and a Temporal Server running with Prometheus metrics enabled.

You can do this by running a [local development Temporal Server](https://docs.temporal.io/cli#start-dev-server) with the following command:

```bash
temporal server start-dev --metrics-port 63626 # this script's default metrics port
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/temporal-sa/temporal-server-actions-count.git
   cd temporal-server-actions-count

2. Install dependencies using Poetry:
    ```bash
    poetry install
    ```

## Usage

The script requires a time window to be specified and can optionally accept a Prometheus URL and namespace for filtering.

Command-line Arguments

`--time-window-seconds`: The time period in seconds over which the total actions will be calculated and reported (required).

`--prometheus-url`: The Prometheus scrape URL. Default is the Temporal development server metrics endpoint: http://localhost:63626/metrics (optional).

`--included-namespace`: The namespace to filter for. Default is all namespaces (optional).

## Examples

With default Prometheus URL and namespace:

```bash
poetry run python temporal-server-actions-count.py --time-window-seconds 120
```

With custom Prometheus URL and namespace:
```bash
poetry run python temporal-server-actions-count.py --time-window-seconds 120 --prometheus-url http://localhost:9090/metrics --included-namespace default
```

## Sample output

```bash
poetry run python temporal-server-actions-count.py --time-window-seconds 10
Starting Prometheus action metric monitoring with a time window of 10 seconds...
Monitoring Prometheus endpoint: http://localhost:63626/metrics
Sampling from all namespaces.
Please wait, the total number of actions will be reported after 10 seconds...
Current average actions per second: 5.00
Current average actions per second: 209.00
Current average actions per second: 106.00
Current average actions per second: 106.00
Current average actions per second: 106.00
Current average actions per second: 53.00
Current average actions per second: 0.00
Current average actions per second: 106.00
Total actions in the last 10 seconds: 691.0
Monitoring completed.
```