**Moaz Murtaza 22I-1902**

**Bilal Bashir 22I-1901**

**Alizeh Qamar 21I-1775**


# Frequent-ItemSet-Analysis-On-Amazon-Metadata

This project implements a real-time product recommendation system for Amazon products using the amazon_metadata dataset. The system leverages streaming data processing techniques to analyze product information and discover frequent itemsets, ultimately suggesting relevant products to customers . 


##### This README provides an overview of the project, including:

- _1.Dataset:_ Description of the amazon_metadata dataset and its structure.

- _2.Pre-processing:_ Steps involved in cleaning and formatting the data for streaming analysis.

- _3.Streaming Pipeline:_ Design of the streaming pipeline with a producer application and multiple consumer applications.
  
- _4.Frequent Itemset Mining:_ Implementation of Apriori and PCY algorithms within consumers to identify frequently co-purchased items.

- _5.Database Integration:_ Integration with a NoSQL database (recommended: MongoDB) to store the discovered frequent itemsets.

- _6.Bonus:_ Bash Script (Optional): Setting up a bash script to automate the execution of producers, consumers, and Kafka components.

This project aims to showcase the application of frequent itemset mining algorithms in a streaming context for real-time product recommendations.


### SAMPLE_SCRIPT

This Python script samples a large JSON file (like Amazon product data) to a smaller size you specify (in gigabytes). It focuses on keeping information relevant to the needs by filtering for specific data fields (like "also_buy" and "categories") and stopping when the target size is reached. It processes the file line by line, keeping track of the output size, and writes chunks of data at a time for efficiency.

### PREPROCESSING AND LOADING OF THE DATASET

This Python script preprocesses a large JSON file containing Amazon product data. It extracts specific features (asin, also_buy, and feature) from each product entry and creates a new JSON file containing only those features. To handle large datasets efficiently, the script processes the data in chunks of 100 rows at a time. Each chunk is converted to JSON format with each product on a separate line and then appended to the output file. This approach reduces memory usage compared to processing the entire file at once.


### PRODUCT DATA STREAMING / PIPELINE WITH KAFKA (producer and the three consumers)

This section describes the producer application, a crucial component in the real-time product recommendation system built using Apache Kafka. The producer continuously reads preprocessed product data from a JSON file _(preprocessed_data.json)_ and streams it to Kafka topics in real-time.

#### Kafka Configuration:

- _bootstrap_servers:_ Specifies the address of the Kafka broker (localhost:9092 in this case).

- _topic:_ Defines the topic name used for streaming "also_buy" data (also-buy-topic).

- _price_topic:_ Defines the topic name used for streaming product feature data (product-price-topic).

- _value_serializer:_ Ensures data sent to Kafka is serialized as JSON strings with UTF-8 encoding for proper data exchange.


#### Data Processing and Streaming:

##### **Batch Creation:**

>The _create_batches_ function reads the preprocessed data file in chunks (batch_size=1000).
 Each chunk (batch) is yielded for further processing.


##### Data Extraction and Transmission:

>- The main loop iterates through batches.
>- Within each batch, the json.loads function parses each line as a JSON object.
>- _The get('also_buy', [])_ method extracts the "also_buy" field (related products) from each JSON object and creates a list (also_buy_batch). Similarly, 
      get('feature', []) extracts product features (feature_batch).


##### Topic-Specific Streaming:

> - The producer sends the also_buy_batch to the also-buy-topic for consumer applications interested in analyzing frequently bought together products.
> - The producer sends the feature_batch to the product-feature-topic for consumer applications focusing on product feature analysis.


##### Confirmation and Delay:

>- _producer.flush()_ ensures all buffered data is sent to Kafka.
>-  _time.sleep(10)_ introduces a 10-second delay between sending batches, simulating real-time data generation.

##### Producer Termination:

>- After processing all batches, the producer closes the connection with producer.close().

##### Consumer Applications 

>- Separate consumer applications will _subscribe to the producer's topics (also-buy-topic and product-feature-topic)_ to receive the streamed data.
>- Consumers can then implement algorithms like Apriori or PCY for real-time frequent itemset mining and generate product recommendations.

### FREQUENT ITEMSET MINING (Consumer Applications for Real-Time Frequent Itemset Mining)

This section describes three consumer applications that subscribe to the "also-buy-topic" created by the producer application. These consumers implement algorithms to discover frequently co-purchased product sets (frequent itemsets) from the streamed data in real-time.

#### Apriori Consumer:

This consumer utilizes the Apriori algorithm, a classic approach for frequent itemset mining. 

##### **Initialization:**

- Defines a support_threshold (minimum number of times items appear together) as 15.

- Establishes a defaultdict (item_frequency) to count individual item occurrences.

- Connects to the Kafka consumer and assigns it to the "also-buy-topic" partition 0.

##### **Batch Processing:**

- iterates through batches of data received from Kafka.

- For each transaction (list of "also-bought" products) in a batch: Counts individual item frequencies.

- Filters infrequent single items based on the support_threshold.

- Generates candidate pairs of frequent items for further analysis.

- Counts the occurrence of each candidate pair within the batch transactions.

- Creates a final dictionary of frequent itemsets that meet the support_threshold.


##### **MongoDB Integration:**

If frequent itemsets are found:

  > - Converts itemset keys to strings (frequent_sets_str_keys) for MongoDB compatibility.
  > -  Stores the batch number (i) and the frequent itemsets (frequent_sets_str_keys) in a MongoDB collection (frequentItemsetsapriori).
  > -  Retrieves the stored document to verify successful insertion.


####  PCY Consumer:

This consumer implements the PCY (Park-Chen-Yu) algorithm, an efficient approach for frequent itemset mining.

##### **Initialization:**

- Defines the number of buckets for hashing (num_buckets) as 10^5.
- Creates a random_hash function to map item pairs to bucket numbers.
- Establishes a defaultdict (bitmap) to count occurrences of item pairs within buckets.
- Sets the support_threshold for frequent itemsets to 15.
- Connects to the Kafka consumer and assigns it to the "also-buy-topic" partition 0.
- Initializes a defaultdict (frequent_itemsets_count) to store final frequent itemset counts.

##### **Batch Processing:**

- Iterates through batches of data received from Kafka.
  
- For each transaction (list of "also-bought" products) in a batch:
  
 >  - Generates all combinations (pairs) of items in the transaction.
 >  -  Hashes each pair using the random_hash function to determine its bucket number.
 > -  Increments the corresponding bucket's count in the bitmap.
  
- Filters the bitmap by setting values to 1 only for buckets with a count exceeding the support_threshold.
- Iterates through transactions again.
  
> For each item pair:
  
> - Retrieves the bucket number using random_hash.
> -  If the bucket's value in the bitmap is 1 (indicating frequent occurrence), increments the count for that pair in frequent_itemsets_count.
  
- Creates a final dictionary of frequent itemsets with counts exceeding the support_threshold.

##### **MongoDB Integration:**

  > - Similar to the Apriori consumer, stores the results (batch number and frequent itemsets) in a separate MongoDB collection (frequentItemsetspcy) for 
         comparison.

### Consumer(Categorizing)

This Third consumer application designed to process a stream of product data from a Kafka topic and categorize them based on their prices in a MongoDB collection.

###### **The Consumer in Action**

>Imports: The code starts by importing necessary libraries for interacting with Kafka (KafkaConsumer, TopicPartition), JSON manipulation (json), and connecting to MongoDB (pymongo).

##### **Configurations:**

> -_bootstrap_servers:_ Defines the address of the Kafka broker (localhost:9092 in this case).

> - _topic_name:_ Specifies the Kafka topic name containing the product data (product-feature-topic).

> -_ mongo_conn_string:_ Sets the connection string for the MongoDB instance (localhost:27017).

> - _mongo_db_name and mongo_collection_name:_ Define the database and collection names within MongoDB where the product data will be stored (product_catalog and products respectively).

> - _MongoDB Connection:_ Establishes a connection to the MongoDB database and creates references to the specific database and collection for storing product information.

##### **Kafka Consumer Setup:**

Creates a Kafka consumer object, specifying the broker addresses and a deserializer function to convert encoded JSON messages into Python dictionaries.
Assigns a specific topic partition **(TopicPartition(topic_name, 0))** to the consumer, indicating which part of the data stream it will process.

##### **Price Categorization Function (categorize_prices):**
> - Takes a product price as input.

> - Based on price ranges, assigns a category label (Budget, Economy, Premium, or Luxury) to the product.


##### **Batch Processing Function (fetch_categorized_products_from_batch):**

> - Takes a batch number as input.

> - Retrieves distinct product categories present in that specific batch from the MongoDB collection.

> - Iterates through each category and fetches product details sorted by price (ascending order).

> - Prints the retrieved product information (ASIN, price, and category) for each product within the category.

##### **Main Loop:**

> - Starts an infinite loop to continuously consume messages from the Kafka topic.

> - For each received message:

> - Prints a message indicating the batch number being processed.

> - Extracts the product data from the message value.

> - Iterates through each product within the data:

> - If the product has a price field:

> - Calls the categorize_prices function to assign a category based on price.

> - Sets the batch number for the product based on the current processing iteration.

> - Uses MongoDB's replace_one method to update the product document in the collection. This performs an upsert operation, meaning it either updates an existing 
   document with the ASIN (unique product identifier) or inserts a new document if it doesn't exist.

> - After processing the products in the batch, calls the fetch_categorized_products_from_batch function to retrieve and print the categorized product details 
    from MongoDB for reference.

> - Increments the batch number for the next iteration.


##### **Overall Functionality**

This consumer acts as a bridge between the real-time product data stream from Kafka and the persistent storage in MongoDB. It continuously processes product information, categorizes them based on price, and stores them in the designated MongoDB collection with additional details like category and batch number. This allows for efficient organization and retrieval of product data with additional insights into price ranges.


### **Why we used the approach of the third consumer (categorizing consumer) and how it is effective : **

> - This approach offers several advantages for the consumer in this scenario. Firstly, by leveraging Kafka's real-time processing capabilities, the consumer application can handle a continuous stream of product data without delays. This ensures that the product information in the MongoDB collection remains up-to-date, reflecting the latest additions or changes. Secondly, categorizing products based on price provides valuable insights for consumers. Imagine browsing an e-commerce platform where products are automatically categorized by price range. This can significantly improve the consumer experience by allowing for quicker product discovery and easier price comparisons within specific budget constraints.

> - In this particular assignment, the consumer application functions as a data pipeline. It processes the product data stream, enriches it with price categories, and stores it in a structured format within MongoDB. This paves the way for further applications that can utilize this categorized product data to enhance the consumer experience. For instance, a recommendation system could leverage these categories to suggest relevant products to consumers based on their browsing history and budget preferences.



##### **Memory Management:**

Both consumers include code to manage memory usage:

  > - Setting data and frequent_sets variables to None after processing each batch.

  > - Calling gc.collect() to encourage garbage collection.
    
Overall, these consumer applications demonstrate the implementation of Apriori and PCY algorithms in a streaming context for real-time discovery of frequent itemsets from product purchase data.


### BASH-SCRIPT 

This batch script automates setting up and running the various components of your real-time product recommendation system. 

##### **Environment Setup:**

> - Sets environment variables for the Kafka directory (KAFKA_DIR) and your project directory (PROJECT_DIR).

##### **Starting Zookeeper:**

> - Opens a new command window ("Zookeeper") and starts the Zookeeper server using the zookeeper-server-start.bat script with the specified configuration file (zookeeper.properties).

> - Waits for 20 seconds to allow Zookeeper to initialize.

##### **Starting Kafka Server:**

> - Opens a separate command window ("Kafka") and starts the Kafka server using the kafka-server-start.bat script with the server configuration file (server.properties).
> - Waits for 20 seconds to allow Kafka to initialize.

##### **Running Producer Script:**

> - Opens another command window ("Producer") and navigates to the project directory (%PROJECT_DIR%).
> - Executes the producer.py script, which presumably reads preprocessed data and streams it to Kafka topics.

##### **Running Consumer Scripts:**

> - Opens two more command windows ("Consumer") each.
> - Navigates them to the project directory (%PROJECT_DIR%).
> - Executes the consumer(PCY).py script in one window, likely implementing the PCY algorithm for frequent itemset mining.
> - Executes the consumer(Apriori).py script in the other window, likely implementing the Apriori algorithm for the same purpose.

##### **Notes:**

> - The script comments out starting a third consumer script (@REM).
> - It concludes by informing you that all services are started and how to stop them manually.

In essence, this script orchestrates the entire system by launching Kafka components (Zookeeper and server), the producer to stream data, and two consumers to analyze the data in real-time using different algorithms.


## CONTRIBUTORS 
> [moaz-murtaza](https://github.com/moaz-murtaza)(i221902@nu.edu.pk)

> [ bilalbashir08](https://github.com/bilalbashir08) (i221901@nu.edu.pk)

> [Alizeh21](https://github.com/Alizeh21)(i211775@nu.edu.pk)



