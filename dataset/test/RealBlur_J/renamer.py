import os
import re

# Define the directory containing the images
directory = "./target"

# Regular expression pattern to match files with names composed only of integers
pattern = re.compile(r"^\d+\.jpg$")

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the filename matches the pattern (only digits before .jpg)
    if pattern.match(filename):
        # Extract the number from the filename (without .jpg)
        number = filename.split('.')[0]
        # Create the new filename with the 'image' prefix
        new_filename = f"image{number}.jpg"
        # Define the full paths for renaming
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed '{filename}' to '{new_filename}'")
