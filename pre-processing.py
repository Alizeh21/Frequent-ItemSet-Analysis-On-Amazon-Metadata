import json
import pandas as pd
 # Columns to use from the JSON
columns = ['asin', 'also_buy'] 
file_path = 'meta_sampled.json'
output_file_name = 'preprocessed_data_head.json'
batch_size = 100

# Function to process each chunk and append it to the output file
def process_chunk(chunk, output_file):

    chunk[columns].to_json(output_file, orient='records', lines=True)
    print(f"Chunk {i}:")
    print(chunk.head())
    print(len(chunk))

# Open the output file in write mode initially
with open(output_file_name, 'w', encoding='utf-8') as outfile:
    # Process each chunk
    for i, chunk in enumerate(pd.read_json(file_path, lines=True, chunksize=batch_size, encoding='utf-8')):
        process_chunk(chunk, outfile)
        # Delete the previous chunk to free memory
        del chunk  
