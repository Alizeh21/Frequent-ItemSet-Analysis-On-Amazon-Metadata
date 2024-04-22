import json
import os
from tqdm import tqdm

def sample_json(input_file, output_file, target_size_gb, filter_keys=['also_buy','categories']):
    target_size_bytes = target_size_gb * 1024**3
    current_size_bytes = 0
    chunk_size = 1000
    buffer = []

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in tqdm(infile):
            record = json.loads(line)
            if any(record.get(key) for key in filter_keys):
                buffer.append(json.dumps(record) + '\n')
                current_size_bytes += len(line.encode('utf-8'))
            if len(buffer) >= chunk_size or current_size_bytes >= target_size_bytes:
                outfile.writelines(buffer)
                buffer.clear()
            if current_size_bytes >= target_size_bytes:
                break
        if buffer:
            outfile.writelines(buffer)

    print(f"Finished sampling. Output size: {current_size_bytes / 1024**3:.2f} GB")


file_path = 'Amazon_Meta.json'
output_file_name = 'Sample_Amazon_Meta.json'

sample_json(file_path,output_file_name,15)