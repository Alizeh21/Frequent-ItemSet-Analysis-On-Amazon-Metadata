from kafka import KafkaConsumer, TopicPartition
import json
import pymongo

bootstrap_servers = ['localhost:9092']
topic_name = 'product-feature-topic'

mongo_conn_string = 'mongodb://localhost:27017/'
mongo_db_name = 'product_catalog'
mongo_collection_name = 'products'

client = pymongo.MongoClient(mongo_conn_string)
db = client[mongo_db_name]
collection = db[mongo_collection_name]

consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

consumer.assign([TopicPartition(topic_name, 0)])


def categorize_prices(price):
    if price < 10000000:
        category = 'Budget'
    elif price < 20000000:
        category = 'Economy'
    elif price < 30000000:
        category = 'Premium'
    else:
        category = 'Luxury'
    return category

def fetch_categorized_products_from_batch(batch_num):
    categories = collection.distinct('category', {'batch_number': batch_num})
    print(f'Fetching categorized products from batch number: {batch_num}')
    for category in categories:
        print(f"Category: {category}")
        for product in collection.find({'batch_number': batch_num, 'category': category}, sort=[('price', pymongo.ASCENDING)]):
            print(f"( ASIN: {product['asin']} - Price: {product['price']:.2f} )", end='\t')
        print()
    print()
    print()

i = 0

for message in consumer:
    print(f'Categorizing prices for batch {i}...')
    products = message.value

    for product in products:
        if product.get('price') is not None:
            product['category'] = categorize_prices(product['price'])
            product['batch_number'] = i
            
            collection.replace_one(
                {'asin': product['asin']},
                product,
                upsert=True 
            )

    
    fetch_categorized_products_from_batch(i)
    i += 1
