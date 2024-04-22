from kafka import KafkaConsumer, TopicPartition
import json
from collections import defaultdict
import pymongo

bootstrap_servers = ['localhost:9092']
topic = 'also-buy-topic'

mongo_conn_string = 'mongodb://localhost:27017/'
mongo_db_name = 'myDatabase'
mongo_collection_name = 'frequentItemsetsapriori'

client = pymongo.MongoClient(mongo_conn_string)
db = client[mongo_db_name]
collection = db[mongo_collection_name]


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
        
        # Convert keys to strings in frequent_sets
        frequent_sets_str_keys = {str(key): value for key, value in frequent_sets.items()}

        # Store the result into MongoDB
        insert_result = collection.insert_one({
            'batch': i,
            'frequent_itemsets': frequent_sets_str_keys
        })

        document_id = insert_result.inserted_id
        print(f'Result stored in MongoDB with document ID: {document_id}')
        
        # Retrieve the result from MongoDB to confirm it was stored correctly
        retrieved_document = collection.find_one({'_id': document_id})
        print('Retrieved from MongoDB:', retrieved_document)

    i += 1
    print()
    print()
