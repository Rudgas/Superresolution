Memory friendly superresolution script using python and hugin

System requirements:
Linux would probably a whole lot easier than using windows.
Hugin (open source panorama software)
Python3
- Python packages: numpy and pillow

For a ~15 Image Stack of 24MP Images:
RAM 6GB or 8GB will be enough for 24MP images (4GB might just cut it)
~6-7GB HDD the tif files are huge
Takes ~12min. on my old i3

There is actually no limit on stack-size concerning RAM when using the average method. Using median, at some point memory could run out (not soon).

How it works:
Step 1: Images are resized to 200% using Bilinear extrapolation (tried several, looked best to me), saved as tif (uncompressed to speed stuff up).
Step 2: Images are aligned using hugin, and cropped to an area all images cover. (this is done on the gpu)
Step 3: Aligned images are sliced into 4 pieces to save on RAM
Step 4: Averages are calculated for all 4 tiles for each pixel
Step 5: Median values are calculated for each pixel (each channel RGB separately)
Step 6: Tiles are stitched back together and the two output files are created and saved in the folder superresolution


How to use it:
Copy the script into any folder, and create a folder inside it called process. Put the images you want to process into this folder. Run the script.
The original files in the folder 'process' won't be modified, however use duplicates.
Don't have anything important running, you might run out of RAM and freeze the system while it tries to shift between ram and swap, or lock up altogether.
Use the console or a program like geany to follow the programs process and the output.

Input filed should be jpg or tif, 16bit images are not supported and will be converted into 8bit automatically.
