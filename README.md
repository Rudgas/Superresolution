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

## How it works
1. Images are resized to 200% using Bilinear extrapolation (tried several, looked best to me), saved as tif (uncompressed to speed stuff up).
2. Images are aligned using hugin, and cropped to an area all images cover. (this is done on the gpu).
3. Aligned images are sliced into 4 pieces to save on RAM.
4. Averages are calculated for all 4 tiles for each pixel.
5. Median values are calculated for each pixel (each channel RGB separately).
6. Tiles are stitched back together and the two output files are created and saved in the folder superresolution.
