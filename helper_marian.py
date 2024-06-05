import os
import subprocess
from openai import OpenAI
import ffmpeg
from PIL import Image
import re
import shutil
import base64

client = OpenAI(api_key="sk-proj-3welySMEaomkDTpHjPY0T3BlbkFJiiAIbZzvlJT3kACsseOR")
conversation_history = []


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_code_block(input_text):
    start_marker = "```python"
    end_marker = "```"
    start = input_text.find(start_marker)
    if start == -1:
        return None
    start += len(start_marker)
    end = input_text.find(end_marker, start)
    if end == -1:
        return None
    return input_text[start:end].strip()

def save_and_run_code(code, required_libraries):
    filename = "extracted_code.py"

    # Fixed configuration code to prepend
    config_code = """
from manim import *

# Configure the output directory and file names
config.media_dir = "./custom_media"
config.video_dir = "./custom_media/videos"
config.images_dir = "./custom_media/images"
config.tex_dir = "./custom_media/Tex"
config.frame_rate = 30
config.pixel_height = 1080
config.pixel_width = 1920
config.save_last_frame = False

"""
    # Combine the configuration code with the extracted code
    full_code = config_code + code
    
    # Write the code to the new file
    with open(filename, "w") as file:
        file.write(full_code)
    
    print("Code saved in file: ", filename)
    # Install required libraries
    print("Installing needed libraries")
    for library in required_libraries:
        subprocess.run(["pip", "install", library], capture_output=True, text=True)
    
    
    if not has_main_function(filename):
        add_main_function(filename)
        print("Added own main function because the beautiful GPT forgot it AGAIN")
        #raise ValueError(f"The file {filename} does not contain a main function.") #Make sure to tell the gpt to integrate a main into its code for automatic code execution

    # Run the new Python file
    print("Executing Code")
    result = subprocess.run(["python", filename], capture_output=True, text=True)
    
    # Print the output of the Python script
    print(result.stdout)
    print(result.stderr)
    
    return result

def get_code_from_openai(prompt, appendend_image=None):
    if appendend_image==None:
        conversation_history.append({"role": "user", "content": prompt})
    else:
        conversation_history.append({
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt,
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{appendend_image}",
                    "detail": "low"
                },
                },
            ],
            }
        )


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation_history,
    )
    response_content = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": response_content})
    return response_content


def print_image_stats(image_path):
    with Image.open(image_path) as img:
        print(f"Image format: {img.format}")
        print(f"Image size: {img.size}")
        print(f"Image mode: {img.mode}")




def extract_frames(video_path, output_dir, video_label):
    # Paths to save the extracted frames
    first_frame_output = os.path.join(output_dir, f"{video_label}_first_frame.jpg")
    last_frame_output = os.path.join(output_dir, f"{video_label}_last_frame.jpg")
    
    # Extract the first frame
    (
        ffmpeg
        .input(video_path, ss=0)
        .output(first_frame_output, vframes=1)
        .run(capture_stdout=True, capture_stderr=True)
    )
    
    # Get video duration
    probe = ffmpeg.probe(video_path)
    duration = float(probe['format']['duration'])
    
    # Calculate the timestamp for the last frame
    frame_rate_str = probe['streams'][0]['r_frame_rate']
    num, denom = map(int, frame_rate_str.split('/'))
    frame_rate = num / denom
    last_frame_time = duration - (1 / frame_rate)
    
    # Extract the last frame
    (
        ffmpeg
        .input(video_path, ss=last_frame_time)
        .output(last_frame_output, vframes=1)
        .run(capture_stdout=True, capture_stderr=True)
    )
    
    return first_frame_output, last_frame_output

def create_combined_image(frame_pairs, output_path):
    # Load the first and last frames for all animations
    images = [(Image.open(first), Image.open(last)) for first, last in frame_pairs]

    # Only include the first frame of the first animation and the last frame of the last animation
    # For intermediate animations, only include their last frames
    if len(images) > 1:
        images = [(images[0][0], images[0][1])] + [(None, img[1]) for img in images[1:-1]] + [(None, images[-1][1])]

    # Determine the final image size
    heights = [img[0].height if img[0] is not None else img[1].height for img in images]
    widths = [img[0].width if img[0] is not None else img[1].width for img in images]
    
    total_width = sum(widths)  # Sum of widths of all images
    max_height = max(heights)  # Maximum height of the images

    combined_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for first_img, last_img in images:
        if first_img is not None:
            combined_image.paste(first_img, (x_offset, 0))
            x_offset += first_img.width
        combined_image.paste(last_img, (x_offset, 0))
        x_offset += last_img.width

    combined_image.save(output_path)


def sort_files_by_last_number(files):
    """ Sort files based on the last numeric part in their names """
    def extract_last_number(filename):
        return int(re.findall(r'\d+', filename)[-1])
    
    return sorted(files, key=extract_last_number)


def get_file_order_from_list(base_dir):
    order_file_path = None
    # Walk through the base directory to find the order file
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == 'partial_movie_file_list.txt':
                order_file_path = os.path.join(root, file)
                break
        if order_file_path:
            break

    if not order_file_path:
        raise FileNotFoundError("partial_movie_file_list.txt not found in any subdirectory.")

    with open(order_file_path, 'r') as file:
        lines = file.readlines()
        # Extract filenames from the order file
        order = [line.split('file:')[-1].strip().replace("'", "").split('/')[-1] for line in lines if line.startswith("file")]
    return order



def extract_images():
    base_dir = os.path.join('custom_media', 'videos', 'partial_movie_files')
    output_dir = os.path.join('custom_media', 'images')
    temp_dir = os.path.join('custom_media', 'temp_videos')
    combined_image_path = os.path.join('custom_media', 'combined_image.jpg')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    animation_count = 1
    frame_pairs = []

    for root, dirs, _ in os.walk(base_dir):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            files = [f for f in os.listdir(dir_path) if f.endswith('.mp4')]
            
            # Get the correct order from partial_movie_file_list.txt
            file_order = get_file_order_from_list(base_dir)
            # Sort files based on the order from the text file
            files_sorted = [file for file in file_order if file in files]

            for i, file in enumerate(files_sorted, 1):
                old_path = os.path.join(dir_path, file)
                new_name = f"anim{i}.mp4"
                new_path = os.path.join(temp_dir, new_name)
                
                # Copy and rename the file
                shutil.copy(old_path, new_path)
                
                try:
                    # Get video duration
                    probe = ffmpeg.probe(new_path)
                    duration = float(probe['format']['duration'])
                    
                    # Check if the video is at least 1 second long
                    if duration >= 1:
                        video_label = f"animation_{animation_count}"
                        first_frame, last_frame = extract_frames(new_path, output_dir, video_label)
                        frame_pairs.append((first_frame, last_frame))
                        animation_count += 1
                except ffmpeg.Error as e:
                    print(f"An error occurred while processing {new_path}: {e}")

    # Create combined image
    create_combined_image(frame_pairs, combined_image_path)
    print(f"Combined image saved at: {combined_image_path}")
    return combined_image_path


# Function to save and run the extracted code block
def save_and_run_extracted_code(code_block):
    required_libraries = ["os", "manim"]  # Add the required libraries here, e.g., ["requests", "numpy"]
    result = save_and_run_code(code_block, required_libraries)
    
    # Check for errors
    if result.returncode != 0:  # Non-zero return code indicates an error
        error_message = result.stderr
        print(f"Error encountered: {error_message}")
        return False, error_message
    return True, None

def extract_and_process_images():
    print("Extracting Images")
    combined_image_path = extract_images()
    print_image_stats(combined_image_path)

    base64_image = encode_image(combined_image_path)

    return base64_image


import ast

def has_main_function(file_path):
    """
    Check if a .py file contains a main function.
    
    Args:
    - file_path (str): The path to the .py file to check.
    
    Returns:
    - bool: True if the file contains a main function, False otherwise.
    """
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        parsed_ast = ast.parse(file_content)
    except SyntaxError as e:
        print(f"Syntax error while parsing the file: {e}")
        return False

    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return True

    return False



def get_first_class_name(file_path):
    """
    Get the name of the first class in a .py file.
    
    Args:
    - file_path (str): The path to the .py file.
    
    Returns:
    - str: The name of the first class if found, None otherwise.
    """
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        parsed_ast = ast.parse(file_content)
    except SyntaxError as e:
        print(f"Syntax error while parsing the file: {e}")
        return None

    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.ClassDef):
            return node.name

    return None


def add_main_function(file_path):
    """
    Add a main function to the end of a .py file based on the first class defined in the file.
    
    Args:
    - file_path (str): The path to the .py file.
    """
    class_name = get_first_class_name(file_path)
    if not class_name:
        raise ValueError(f"No class found in the file {file_path}.")

    main_function_code = f"""
if __name__ == "__main__":
    scene = {class_name}()
    scene.render()
"""

    with open(file_path, "a") as file:
        file.write(main_function_code)

    print(f"Main function added to {file_path}")