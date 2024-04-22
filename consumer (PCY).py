from kafka import KafkaConsumer, TopicPartition  
import json
import gc
from itertools import combinations
from collections import defaultdict


## Defining kafka consumer configuration 
bootstrap_servers = ['localhost:9092']
topic = 'also-buy-topic'

## number of buckets for the pcy algorithm 
num_buckets = 10**5

## Generating the hash values for the items 
def random_hash(item):
    return hash(item) % num_buckets

## Function to process a batch of data and finding 
# the frequent-itemsets using pcy
def process_batch(batch):  
    
    # initializing bitmap to count the number of occurances of each pair 
    bitmap = defaultdict(int)
    for sublist in batch:
        for pair in combinations(sublist, 2):
            bucket_number = random_hash(pair)
            bitmap[bucket_number] += 1

## Threshold for frequent-itemset 
    support_threshold = 15

#Setting the bitmap value to 1 for the buckets that meet the  threshold
    for key in bitmap.keys():
        bitmap[key] = 1 if bitmap[key] >= support_threshold else 0

#initializing the dictionary to count the frequent itemsets
    frequent_itemsets_count = defaultdict(int)

#counting the number of frequent itemsets in the batch
    for sublist in batch:
        for pair in combinations(sublist, 2):
            bucket_number = random_hash(pair)
            if bitmap[bucket_number] == 1:
                frequent_itemsets_count[pair] += 1

#Returning the frequent itemsets that meet the threshold
    final_frequent_itemsets = {
        itemset: count for itemset, count in frequent_itemsets_count.items() 
        if count >= support_threshold
    }

    return final_frequent_itemsets
        
        
#Initializing the kafka consumer
consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))
#Assignning the consumer to the specified topic and partition
consumer.assign([TopicPartition(topic, 0)])

#Counter for the number of batches processed
i = 0

#Processing Each message in the kafka topic
for message in consumer:
    print(f'Computing PCY Frequent Dataset for {i} batch:')
    data = message.value
    #process the batch using the pcy algorithm 
    frequent_sets = process_batch(data)
    
    #printing the frequent itemsets found in the batch
    if frequent_sets is not None:
        print(frequent_sets)
    
    #free the memory by setting the variables
    # data annd frequent sets to none
    data = None
    frequent_sets = None
    
    #Run the garbage collector to free up memory
    gc.collect() 
    #blank lines for separate output of each batch
    print()
    print()
    
    #increment the batch counter 
    i+=1