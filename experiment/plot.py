import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('/home/fzhg/code/ECE750/project/code/Adaptive-Circuit-Breaking/istio_max_connections.csv')

# Convert the 'Timestamp' column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Plot the data
plt.plot(df['Timestamp'], df['Max Connections'])
plt.xlabel('Timestamp')
plt.ylabel('Max Connections')
plt.title('Max Connections over Time')
plt.xticks(rotation=45)
plt.show()