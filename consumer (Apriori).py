from kafka import KafkaConsumer, TopicPartition
import json
from collections import defaultdict

bootstrap_servers = ['localhost:9092']
topic = 'also-buy-topic'

def process_batch(batch):
    support_threshold = 15
    item_frequency = defaultdict(int)

    # Count frequency of individual items
    for transaction in batch:
        unique_items = set(transaction)
        for item in unique_items:
            item_frequency[item] += 1

    # Filter out infrequent single items and prepare frequent itemset dictionary
    frequent_items = {item for item, count in item_frequency.items() if count >= support_threshold}
    
    # Generate candidate pairs
    candidates = [(item1, item2) for item1 in frequent_items for item2 in frequent_items if item1 < item2]

    # Count frequency of candidate pairs
    candidate_counts = defaultdict(int)
    for sublist in batch:
        sublist_set = set(sublist)
        for candidate in candidates:
            if all(item in sublist_set for item in candidate):
                candidate_counts[candidate] += 1

    # Compile final list of frequent itemsets with sufficient support
    final_frequent_itemsets = {
        itemset: count for itemset, count in candidate_counts.items() if count >= support_threshold
    }

    return final_frequent_itemsets

consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

consumer.assign([TopicPartition(topic, 0)])

i = 0

for message in consumer:
    print(f'Computing Apriori Frequent Dataset for batch {i}:')
    data = message.value
    frequent_sets = process_batch(data)
    if frequent_sets:
        print(frequent_sets)
    print()
    print()
