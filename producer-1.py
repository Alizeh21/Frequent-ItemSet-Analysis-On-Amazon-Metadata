import json
import time
from kafka import KafkaProducer

#Define the path to the preprocessed file 
file_path = 'preprocessed_data.json'

#Define kafka producer configuration
bootstrap_servers = ['localhost:9092']
topic = 'also-buy-topic'
feature_topic = 'product-feature-topic'
#Initializing the producer 
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Defining the batch size and the slide size for sending the data to kafka
batch_size = 1000
slide = 500

#Reading the preprocessed data 
def create_batches(file_path, batch_size):
    with open(file_path, 'r') as file:
        batch = []       
        for line in file:
            batch.append(line)
            if len(batch) == batch_size:
                yield batch
                batch = []
        # Don't forget to yield the last batch if it's smaller than the batch size
        if batch:
            yield batch

# Process and send batches of data
for batch in create_batches(file_path, batch_size):    
    #extracting the also-buy field from each line in the batch
    also_buy_batch = [json.loads(line).get('also_buy', []) for line in batch]
    feature_batch = [json.loads(line).get('feature', []) for line in batch]
    #sending the batch of data
    producer.send(topic, also_buy_batch)
    print(f"send topic with batch : {also_buy_batch}")
    producer.send(feature_topic, feature_batch)
    print(f"Sent batch to {feature_topic}: {len(feature_batch)} records sent.")
    
    producer.flush()
    
    #Adding delay before sending the next batch
    time.sleep(10)

producer.close()
