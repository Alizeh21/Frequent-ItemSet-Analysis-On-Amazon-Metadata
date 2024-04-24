import json
import time
from kafka import KafkaProducer

file_path = 'preprocessed_data.json'
bootstrap_servers = ['localhost:9092']
also_buy_topic = 'also-buy-topic'
feature_topic = 'product-feature-topic'

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

batch_size = 1000
slide = 500

def create_batches(file_path, batch_size):
    with open(file_path, 'r') as file:
        batch = []
        for line in file:
            batch.append(line)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

# Process and send batches of data
for batch in create_batches(file_path, batch_size):
    also_buy_batch = [json.loads(line).get('also_buy', []) for line in batch]
    
    feature_batch = [
    {
        'asin': json.loads(line).get('asin'),
        'price': json.loads(line).get('price')
    }
    for line in batch
    if 'asin' in line and
       json.loads(line).get('price') is not None and
       isinstance(json.loads(line).get('price'), (int, float)) and
       json.loads(line).get('price') <= 10000000000
    ]

    # Send also_buy data to also-buy-topic
    producer.send(also_buy_topic, also_buy_batch)
    print(f"Sent batch to {also_buy_topic}: {len(also_buy_batch)} records sent.")

    # Send feature data to product-feature-topic
    producer.send(feature_topic, feature_batch)
    print(f"Sent batch to {feature_topic}: {len(feature_batch)} records sent.")

    producer.flush()
    time.sleep(10)

producer.close()
