import csv
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import subprocess
import json
from datetime import datetime

def query_istio_destinationrule(rule_name):
    # Adjust this command based on your setup and access methods.
    command = f"kubectl get destinationrule {rule_name} -o json"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        print(f"Error querying Istio: {result.stderr}")
        return None
    return json.loads(result.stdout)

def save_to_csv(data, filename):
    with open(filename, 'a', newline='') as file:  # 'a' to append data
        writer = csv.writer(file)
        writer.writerow(data)

def plot_data(filename):
    timestamps = []
    max_connections = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamps.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            max_connections.append(int(row[1]))

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, max_connections, marker='o')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xlabel('Timestamp')
    plt.ylabel('Max Connections')
    plt.title('Time Series of Max Connections in Istio DestinationRule: httpbin')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

#Main script
rule_name = "httpbin"
filename = "istio_max_connections.csv"

# Write header to CSV file
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Max Connections'])

# Query Interval (in seconds)
query_interval = 2  # Query every 60 seconds

try:
    while True:
        result = query_istio_destinationrule(rule_name)
        if result:
            max_conn = result.get('spec', {}).get('trafficPolicy', {}).get('connectionPool', {}).get('tcp', {}).get('maxConnections')
            if max_conn is not None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_to_csv([timestamp, max_conn], filename)
        
        time.sleep(query_interval)
except KeyboardInterrupt:
    print("Stopped querying. Plotting data.")
    plot_data(filename)
