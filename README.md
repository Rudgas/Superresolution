# Memory Friendly Superresolution Script

This is a python script to create averages or median values along a stack of images.
By increasing the scale prior to alignment, sub-RGB-pixel resolution can be achieved exploiting minute shifts of light across the image sensors bayer pattern.

### Prerequisites

The following programs and python packages are needed:

- Hugin
- Python 3
  - numpy
  - scikit-image
  - Pillow

Python packages can be installed either through your distribution e.g. *buntu/debian:
```
sudo apt install python3-skimage
```
Please note that for different distributions packages might be called differently. Also make sure you are getting the python 3 version of all packages.

Or through pythons own package installer pip e.g.:
```
pip3 install --user scikit-image numpy pillow
```

### Installing

The script can be run from any folder, please make sure you have a subfolder called "process" in which you place your image-stack.

```
git clone https://github.com/Rudgas/Superresolution.git
cd Superresolution
mkdir process
```

## Getting Started

Copy a stack of images into the folder process, for a typical application use handheld or tripod burst shots. 5 Images minimum are recommended.
Images can be of format jpg or tif, in 8bit or 16bit.

**A word of caution: For 8bit 24MP image-stacks at least 4GB of free RAM are needed. And approximately 0.5GB of HDD space per image.
For 16bit images at least 6GB of free RAM is needed.**

Run the script in a terminal (or use the editor geany -> execute) to follow the progress.
```
python3 Superresolution.py
```
If everything went well, a folder called superresolution will be created, containing two images, one for median and one for the average method.




Expected Input:
- A folder called 'process' in the same folder the script is in
- Images inside the folder process of the following formats:
8bit or 16bit *.tif *.TIF *.tiff *.TIFF *.jpg *.JPG
- Images that are very similar. Best results using handheld burst mode or tripod

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
