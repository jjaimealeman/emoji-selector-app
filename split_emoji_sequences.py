import math

def split_file(input_file, lines_per_file=100):
    with open(input_file, 'r') as infile:
        data = infile.readlines()
    
    total_lines = len(data)
    num_files = math.ceil(total_lines / lines_per_file)
    
    for i in range(num_files):
        start = i * lines_per_file
        end = min((i + 1) * lines_per_file, total_lines)
        
        with open(f'emoji_sequences_part_{i+1}.json', 'w') as outfile:
            outfile.writelines(data[start:end])

    print(f"Split {input_file} into {num_files} files.")

if __name__ == "__main__":
    split_file("emoji-sequences-copy.json")
