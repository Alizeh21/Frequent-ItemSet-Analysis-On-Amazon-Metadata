import json
import time
from kafka import KafkaProducer

#Define the path to the preprocessed file 
file_path = 'preprocessed_data.json'

#Define kafka producer configuration
bootstrap_servers = ['localhost:9092']
topic = 'also-buy-topic'

#Initializing the producer 
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Defining the batch size and the slide size for sending the data to kafka
batch_size = 1000
slide = 500

#Reading the preprocessed data 
with open(file_path, 'r') as file:
    lines = file.readlines()

# Send batches of data to kafka (1000 lines)
for i in range(0, len(lines), slide):
    batch = lines[i:i+batch_size]
    
    #extracting the also-buy field from each line in the batch
    also_buy_batch = [json.loads(line).get('also_buy', []) for line in batch]
    
    #sending the batch of data
    producer.send(topic, also_buy_batch)
    print(f"send topic with batch : {also_buy_batch}")
    producer.flush()
    
    #Adding delay before sending the next batch
    time.sleep(10)

producer.close()
