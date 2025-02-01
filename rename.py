import os
import re
import sys
import exifread
import ffmpeg
import shutil

# Target format for all files:
# YYYYMMDD_HHMMSS.ending

# Directory with Images and Videos
input_directory = 'path\\to\\input'
output_directory = 'path\\to\\output'

# Dictionary to store new and old file names
file_dict = {}

# Operating mode:
# 'copy' = The original is left untouched and the files get copied to the output directory
# 'inplace' = The original files are renamed
mode = 'inplace'

# Part of the name that should be removed (order matters, the version with underscore always goes first)
to_replace = ['IMG_', 'IMG-', 'IMG', 'VID_', 'VID-', 'VID', 'PXL_', 'PXL-', 'PXL', '_iOS']

# Image formats
img_formats = ('.jpg', '.jpeg', '.png', '.heic')

# Video formats
vid_formats = ('.mp4', '.mov')

# Initialize counters:
count_success = 0
count_copied = 0
count_failure = 0
count_all = 0

# Regex patterns
correct_pattern = r'^\d{8}_\d{6}\.\w+$'
missing_underscore_pattern = r'^(\d{8})(\d{6})(\.\w+)$'
unnecessary_chars_pattern = r'^\d{8}_\d{6}'
wrong_underscore_pattern = r'^(\d{8})(\d{6})_(\d{8})(\d{6})(\.\w+)$'
too_many_underscore_pattern = r'^(\d{8})(\d{6})_(\d+)_(\d{8})(\d{6})(\.\w+)$'

# Define output colors
CYELLOW = '\33[33m'
CEND = '\33[0m'


# extract the DateTimeOriginal field from an image
def get_exif_DateTimeOriginal(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)
        for tag in tags:
            if tag == 'EXIF DateTimeOriginal':
                return str(tags[tag])


# extract the creation_time field from a video
def get_video_metadata_creation_date(video_path):
    probe = ffmpeg.probe(video_path)
    creation_time = None
    for stream in probe['streams']:
        if 'tags' in stream and 'creation_time' in stream['tags']:
            creation_time = stream['tags']['creation_time']
    return creation_time


def rename_img_using_metadata():
    image_path = os.path.join(input_directory, file)
    extension = os.path.splitext(file)[1]
    exif_DateTimeOriginal = get_exif_DateTimeOriginal(image_path)
    if exif_DateTimeOriginal is not None:
        date_str = exif_DateTimeOriginal.replace(':', '').replace(' ', '_')
        new_filename = f"{date_str}{extension}"
        return new_filename
    else:
        return file


# Function to rename Whatsapp Images copied from a chat using metadata
def whatsapp_image_renamer():
    return rename_img_using_metadata()


# Function to rename screenshots
def screenshot_renamer():
    match_screenshot = re.match(r'Screenshot_(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})-\d{2}_[a-z0-9]+\.\w+', file)
    date_str = match_screenshot.group(1)
    time_str = match_screenshot.group(2) + match_screenshot.group(3) + match_screenshot.group(4)
    extension = os.path.splitext(file)[1]
    new_filename = f"{date_str.replace('-', '')}_{time_str}{extension}"
    return new_filename


# Function to rename iphone images using metadata
def iphone_image_renamer():
    return rename_img_using_metadata()


# Function to rename videos using metadata
def video_renamer():
    video_path = os.path.join(input_directory, file)
    file_extension = os.path.splitext(file)[1]
    creation_time = get_video_metadata_creation_date(video_path)
    if creation_time:
        date_str = creation_time.replace('-', '').replace(':', '').replace('T', '_').split('.')[0]
        new_filename = f"{date_str}{file_extension}"
        return new_filename
    else:
        return file


# Function to wait for feedback from the user
def wait_for_user_input():
    while True:
        user_input = input("Press 'Y' to apply the new names or 'N' to stop: ").strip().upper()
        if user_input == 'Y':
            break
        elif user_input == 'N':
            print("Stopping without renaming...")
            exit(2)
        else:
            print("Invalid input. Please press 'Y' to continue or 'N' to stop.")


# Function to print out all necessary renamings as a table
def print_dict_as_table(dictionary):
    # Print the table header
    print('The following table shows all files with name changes in yellow:')
    print(f"{'Old filename':<75} | {'New filename':<30}")
    print("-" * 108)

    # Print each key-value pair in the dictionary
    for key, value in dictionary.items():
        if key != value:
            print(CYELLOW + f"{key:<75}" + CEND + " | " + CYELLOW + f"{value:<30}" + CEND)
        else:
            print(f"{key:<75} | {value:<30}")


# Function to apply the renaming stored in the dict
def rename_files(dictionary):
    count_s = 0
    count_f = 0
    count_c = 0

    for key, value in dictionary.items():
        try:
            if mode == 'copy':
                shutil.copy2(os.path.join(input_directory, key), os.path.join(output_directory, value))
            elif mode == 'inplace':
                os.rename(os.path.join(input_directory, key), os.path.join(output_directory, value))
            else:
                print("Unknown operation mode! Exiting the program...")
                sys.exit(9)

            if key == value:
                count_c += 1
            else:
                count_s += 1
        except:
            count_f += 1

    return count_s, count_c, count_f


# Main Sequence:
# Set output correctly if inplace mode is used:
if mode == 'inplace':
    output_directory = input_directory

# Go through the input directory and rename images
for file in os.listdir(input_directory):
    file_type = None
    new_filename = None
    count_all += 1
    # Check for the correct ending
    if file.lower().endswith(img_formats) or file.lower().endswith(vid_formats):
        # Check for special cases: WhatsApp files (works only if metadata is included)
        if 'WhatsApp' in file or '-WA' in file:
            file_type = 'WhatsApp file'
            if file.lower().endswith(img_formats):
                new_filename = whatsapp_image_renamer()
            elif file.lower().endswith(vid_formats):
                new_filename = video_renamer()
        # Check for special cases: Screenshot
        elif 'Screenshot' in file:
            file_type = 'Screenshot'
            new_filename = screenshot_renamer()
        # Check for special cases: Snapchat
        elif 'Snapchat' in file:
            file_type = 'Snapchat file'
            # Snapchat videos contain the creation_time as metadata
            if file.lower().endswith(vid_formats):
                new_filename = video_renamer()
            # Snapchat images do not contain any necessary information
            elif file.lower().endswith(img_formats):
                new_filename = file
                count_copied += 1
        # Check for special cases: Iphone Image
        elif 'IMG_' and file.lower().endswith('.heic'):
            file_type = 'Iphone image'
            new_filename = iphone_image_renamer()
        # Check for special cases: Iphone Video
        elif file.lower().endswith('.mov'):
            file_type = 'Iphone video'
            new_filename = video_renamer()
        # Normal format, only some parts need to be removed
        else:
            file_type = 'file'
            new_filename = file
            for part in to_replace:
                new_filename = new_filename.replace(part, '')

        # check if additional truncation needs to be done
        correct_match = re.match(correct_pattern, new_filename)
        if not correct_match:
            missing_underscore_match = re.match(missing_underscore_pattern, new_filename)
            unnecessary_chars_match = re.match(unnecessary_chars_pattern, new_filename)
            wrong_underscore_match = re.match(wrong_underscore_pattern, new_filename)
            too_many_underscore_match = re.match(too_many_underscore_pattern, new_filename)

            if missing_underscore_match:
                new_filename = missing_underscore_match.group(1) + '_' + missing_underscore_match.group(
                    2) + missing_underscore_match.group(3)

            if unnecessary_chars_match:
                new_filename = unnecessary_chars_match.group() + os.path.splitext(new_filename)[1]

            if wrong_underscore_match:
                new_filename = wrong_underscore_match.group(1) + '_' + wrong_underscore_match.group(
                    2) + wrong_underscore_match.group(5)
            if too_many_underscore_match:
                new_filename = too_many_underscore_match.group(1) + '_' + too_many_underscore_match.group(
                    2) + too_many_underscore_match.group(6)

        # Check if the new name is unique or if a suffix needs to be applied
        unique_name = new_filename
        counter = 1
        while unique_name in file_dict.values():
            base, extension = os.path.splitext(new_filename)
            unique_name = f"{base} ({counter}){extension}"
            counter += 1
        file_dict[file] = unique_name


# Show the result of the renaming
print_dict_as_table(file_dict)

# Ask the user before applying
wait_for_user_input()

# apply the renaming
count_success, count_copied, count_failure = rename_files(file_dict)

# Print final statistics
print("\nAll image- and videofiles processed!")
print(f"{count_all} images processed: {count_success} successful renamings, {count_copied} copied without renaming"
      f", {count_failure} failures while copying/renaming, {count_all - (count_success + count_copied + count_failure)}"
      f" not processed")