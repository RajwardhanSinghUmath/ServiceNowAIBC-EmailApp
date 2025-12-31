import csv
import random

input_file = 'urldata.csv'
output_file = 'random_good_urls.txt'

good_urls = []

with open(input_file, mode='r', encoding='utf-8') as f_in:
    reader = csv.DictReader(f_in)
    for row in reader:
        if row['label'].strip().lower() == 'good':
            good_urls.append(row['url'])

num_to_sample = min(len(good_urls), 100)
random_selection = random.sample(good_urls, num_to_sample)

with open(output_file, mode='w', encoding='utf-8') as f_out:
    for url in random_selection:
        f_out.write(url + "\n")

print(f"Extracted {len(random_selection)} random 'good' URLs to {output_file}.")