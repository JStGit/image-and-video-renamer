# Image-and-Video-Renamer
Different smartphone manufacturers follow different naming conventions for their images and videos. 
For example, a picture taken at the exact same time with different smartphones will result in the following file names, just to name a few:
| Smartphone Manufacturer| File Name|
|  --------  |  -------  |
| Samsung Galaxy S23|  20250101_010203.jpg
| Apple Iphone 11| IMG_0001.HEIC |
| Google Pixel 8|PXL_20250101_010203000.RAW-01.COVER.jpg |
| OnePlus 12| IMG20250101010203.jpg |

If we further include screenshots or images exported from social media apps like WhatsApp, it gets even more confusing. This is rather unhelpful when combining images and videos from multiple sources to display them together as it will be most likely impossible to show them in the correct order.

This tool uses the names of the files and metadata to rename images and videos to the yyyymmdd_hhmmss.ending convention as this is most easily sortable, as sorting by name is a universal feature.

# Usage
Put the path to the files that should be processed in **input_directory** in line 12. 
Secondly, put the output path in **output_directory** in the next line.
Furthermore, the program features two modes of operation that can be set in line 21. By default, the program operates in copy mode where the original images are not changed and the renamed files are copied to the output directory. If inplace mode is selected, all changes are made to the original files.

The program can now be run. The program will first create all new names and will display all old and new names side by side in a table. Names that have changed are shown in yellow. The user can then accept the changes with 'Y' to apply them or deny them with 'N'.

# Known issues
 - Snapchat images do not include useful metadata or a timestamp in their name, so they cannot be renamed
 - WhatApp files that are exported from a chat also do not include useful metadata and cannot be renamed
