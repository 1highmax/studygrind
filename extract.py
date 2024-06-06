import os
import tiktoken


def extract_manim_scripts(directory, output_file):
    # List of file extensions to check
    file_extensions = ['.py', '.rst']
    # The string to search for in files
    search_string = 'from manim import *'
    
    with open(output_file, 'w') as outfile:
        # Walk through the directory tree
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if the file has the right extension
                if any(file.endswith(ext) for ext in file_extensions):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as infile:
                        content = infile.read()
                        # Check if the search string is in the content
                        if search_string in content:
                            outfile.write(f'# Extracted from {filepath}\n')
                            outfile.write(content)
                            outfile.write('\n\n')
                            

def count_tokens_in_file(file_path, encoding_name='cl100k_base'):
    """Count the number of tokens in the given file."""
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Get the encoding
    encoding = tiktoken.get_encoding(encoding_name)

    # Encode the content to get tokens
    tokens = encoding.encode(content)

    # Return the number of tokens
    return len(tokens)

# Directory containing the .py files
input_directory = '/Users/hochmax/learn/manim'
# Output file to store the extracted scripts
output_file = 'manim_docs.py'

# Extract the manim scripts
extract_manim_scripts(input_directory, output_file)
token_count = count_tokens_in_file(output_file)
print(f"tokens: {token_count}")

