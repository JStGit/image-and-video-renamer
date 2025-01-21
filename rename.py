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

# Operating mode:
# 'copy' = The original is left untouched and the files get copied to the output directory
# 'inplace' = The original files are renamed
mode = 'inplace'

# Part of the name that should be removed (order matters, the version with underscore always goes first)
to_replace = ['IMG_', 'IMG-', 'IMG', 'VID_', 'VID-', 'VID', 'PXL_', 'PXL-', 'PXL', '_iOS']

# Image formats
img_formats = ('.jpg', '.jpeg', '.png', '.HEIC')

# Video formats
vid_formats = ('.mp4', '.MOV')

# Initialize counters:
count_success = 0
count_snapchat = 0
count_failure = 0
count_all = 0

# Regex patterns
correct_pattern = r'^\d{8}_\d{6}\.\w+$'
missing_underscore_pattern = r'^(\d{8})(\d{6})(\.\w+)$'
unnecessary_chars_pattern = r'^\d{8}_\d{6}'
wrong_underscore_pattern = r'^(\d{8})(\d{6})_(\d{8})(\d{6})(\.\w+)$'


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


# Function to rename Whatsapp Images downloaded from a chat
def whatsapp_saved_renamer():
    match_whatsapp = re.match(r'WhatsApp Image (\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2})\.jpeg', file)
    date_str = match_whatsapp.group(1)
    time_str = match_whatsapp.group(2).replace('.', '')
    new_filename = f"{date_str.replace('-', '')}_{time_str}.jpeg"
    return new_filename


# Function to rename Whatsapp Images copied from a chat using metadata
def whatsapp_chat_renamer():
    image_path = os.path.join(input_directory, file)
    exif_DateTimeOriginal = get_exif_DateTimeOriginal(image_path)
    if exif_DateTimeOriginal is not None:
        date_str = exif_DateTimeOriginal.replace(':', '').replace(' ', '_')
        new_filename = f"{date_str}.jpeg"
        return new_filename
    else:
        return None


# Function to rename screenshots
def screenshot_renamer():
    match_screenshot = re.match(r'Screenshot_(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})-\d{2}_[a-z0-9]+\.jpg', file)
    date_str = match_screenshot.group(1)
    time_str = match_screenshot.group(2) + match_screenshot.group(3) + match_screenshot.group(4)
    new_filename = f"{date_str.replace('-', '')}_{time_str}.jpg"
    return new_filename


# Function to rename iphone images using metadata
def iphone_image_renamer():
    image_path = os.path.join(input_directory, file)
    exif_DateTimeOriginal = get_exif_DateTimeOriginal(image_path)
    if exif_DateTimeOriginal is not None:
        date_str = exif_DateTimeOriginal.replace(':', '').replace(' ', '_')
        new_filename = f"{date_str}.HEIC"
        return new_filename
    else:
       return None


# Function to rename iphone videos using metadata
def iphone_video_renamer():
    video_path = os.path.join(input_directory, file)
    creation_time = get_video_metadata_creation_date(video_path)
    if creation_time:
        date_str = creation_time.replace('-', '').replace(':', '').replace('T', '_').split('.')[0]
        new_filename = f"{date_str}.mov"
        return new_filename
    else:
        return None


# Function to rename iphone videos using metadata
def snapchat_video_renamer():
    video_path = os.path.join(input_directory, file)
    creation_time = get_video_metadata_creation_date(video_path)
    if creation_time:
        date_str = creation_time.replace('-', '').replace(':', '').replace('T', '_').split('.')[0]
        new_filename = f"{date_str}.mp4"
        return new_filename
    else:
        return None


# Go through the input directory and rename images
for file in os.listdir(input_directory):
    image_type = None
    new_filename = None
    count_all += 1
    # Check for the correct ending
    if file.endswith(img_formats) or file.endswith(vid_formats):
        # Check for special cases: WhatsApp saved from chat
        if 'WhatsApp' in file:
            image_type = 'WhatsApp (exported) file'
            new_filename = whatsapp_saved_renamer()
        # Check for special cases: WhatsApp internal naming
        elif '-WA' in file:
            image_type = 'WhatsApp (chat) file'
            new_filename = whatsapp_chat_renamer()
        # Check for special cases: Screenshot
        elif 'Screenshot' in file:
            image_type = 'Screenshot'
            new_filename = screenshot_renamer()
        # Check for special cases: Snapchat
        elif 'Snapchat' in file:
            image_type = 'Snapchat file'
            # Snapchat videos contain the creation_time as metadata
            if file.lower().endswith(vid_formats):
                new_filename = snapchat_video_renamer()
            # Snapchat images do not contain any necessary information
            elif file.lower().endswith(img_formats):
                new_filename = file
                count_snapchat += 1
        # Check for special cases: Iphone Image
        elif file.lower().endswith('.heic'):
            image_type = 'Iphone image'
            new_filename = iphone_image_renamer()
        # Check for special cases: Iphone Video
        elif file.lower().endswith('.mov'):
            image_type = 'Iphone video'
            new_filename = iphone_video_renamer()
        # Normal format, only some parts need to be removed
        else:
            image_type = 'file'
            new_filename = file
            for part in to_replace: 
                new_filename = new_filename.replace(part, '')

        # check if additional truncation needs to be done
        correct_match = re.match(correct_pattern, new_filename)
        if not correct_match:
            missing_underscore_match = re.match(missing_underscore_pattern, new_filename)
            unnecessary_chars_match = re.match(unnecessary_chars_pattern, new_filename)
            wrong_underscore_match = re.match(wrong_underscore_pattern, new_filename)

            if missing_underscore_match:
                new_filename = missing_underscore_match.group(1) + '_' + missing_underscore_match.group(
                    2) + missing_underscore_match.group(3)

            if unnecessary_chars_match:
                new_filename = unnecessary_chars_match.group() + os.path.splitext(new_filename)[1]

            if wrong_underscore_match:
                new_filename = wrong_underscore_match.group(1) + '_' + wrong_underscore_match.group(
                    2) + wrong_underscore_match.group(5)

        # Rename the image and copy it
        if new_filename is not None:
            try:
                if mode == 'copy':
                    shutil.copy2(os.path.join(input_directory, file), os.path.join(output_directory, new_filename))
                elif mode == 'inplace':
                    os.rename(os.path.join(input_directory, file), os.path.join(input_directory, new_filename))
                else:
                    print("Unknown operation mode! Exiting the program...")
                    sys.exit(9)
                if file is not new_filename:
                    count_success += 1
                print(f"Processed {image_type}: {file} -> {new_filename}")
            except:
                count_failure += 1
                print(f"Error renaming {image_type}: {file}")
        else:
            count_failure += 1
            print(f"Metadata error {image_type}: {file}")

# Print final statistics
print("\nAll image- and videofiles processed!")
print(f"{count_all} images processed: {count_success} successful renamings, {count_failure} failed renamings, {count_snapchat} snapchat file(s) copied,"
      f" {count_all - (count_success + count_failure + count_snapchat)} not processed")