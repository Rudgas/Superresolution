#!/usr/bin/env python3

import os
import numpy as np
from skimage import io, transform
from PIL import Image
import pyvips

def main():
	### setup ###
	#configure extrapolation methods in the future
	

	
	
	
	
	#resize images to 200%
	resize()
	#call hugin to do an alignment, crop to common covered area
	align()
	#split images into 4 tiles
	tile()
	#calculate average for each pixel
	average()
	#calculate median for each pixel
	median()
	#stitch all 4 tiles back together
	stitch()
	
	print("Done!")
	 
def resize():
	#check if directories are present
	print("----- Resizing Images -----")
	if os.path.exists("./process"):
		os.chdir("./process")
	else:
		print("Please create a folder 'process' and add images that are to be processed")
		exit()
	
	if not os.path.exists("./resized"):
		os.mkdir("./resized")
	
	#get a list of all files, check if more than one file is available
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	N = len(imlist)
	if N <= 1:
		print("Please use more than one image File")
		exit()
		
	for i in range(N):
		print("Resizing: " + imlist[i])
		img = pyvips.Image.new_from_file(imlist[0], access='sequential')
		out = img.resize(2, kernel = "mitchell") #nearest linear cubic mitchell lanczos2 lanczos3
		out.write_to_file("./resized/" + imlist[i][:-4] + "_resized.tif")
	
	#return to parent directory
	os.chdir("..")
	
def align():
	print("----- Aligning Images -----")
	#use hugin for alignment of images
	os.chdir("./process/resized")
	os.system("align_image_stack --use-given-order -C -x -y -z -a aligned_ --corr=0.8 -t 1 -c 100 -v --gpu *.tif") #try scale option
	os.system("rm *_resized.tif")
	os.chdir("../..")

def tile():
	print("----- Tiling Images -----")
	os.chdir("./process/resized")
	#create folders for the 4 tiles
	for i in range(4):
		if not os.path.exists("tile"+str(i)):
			os.mkdir("tile"+str(i))
	
	#get list of image files
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	N = len(imlist)
	
	#get image dimensions (all images are the same size after aligning
	img = pyvips.Image.new_from_file(imlist[0], access='sequential')
	h = img.height
	w = img.width
	
	for i in range(N):
		print("Tiling: " + imlist[i])
		
		img = pyvips.Image.new_from_file(imlist[i], access='sequential')
		img = img[0:img.bands - 1]
		tile = img.crop(0,0,int(w/2),int(h/2)) #left, top, width, height
		tile.write_to_file("./tile0/" + imlist[i][:-4] + "_tile0.tif")
		
		img = pyvips.Image.new_from_file(imlist[i], access='sequential')
		img = img[0:img.bands - 1]
		tile = img.crop(0,int(h/2),int(w/2), h - int(h/2)) #left, top, width, height
		tile.write_to_file("./tile1/" + imlist[i][:-4] + "_tile1.tif")
		
		img = pyvips.Image.new_from_file(imlist[i], access='sequential')
		img = img[0:img.bands - 1]
		tile = img.crop(int(w/2),0,w - int(w/2),int(h/2)) #left, top, width, height
		tile.write_to_file("./tile2/" + imlist[i][:-4] + "_tile2.tif")
		
		img = pyvips.Image.new_from_file(imlist[i], access='sequential')
		img = img[0:img.bands - 1]
		tile = img.crop(int(w/2),int(h/2),w - int(w/2),h - int(h/2)) #left, top, width, height
		tile.write_to_file("./tile3/" + imlist[i][:-4] + "_tile3.tif")		
		
	#remove aligned images
	os.system("rm align*")
	os.chdir("../..")
	
def average():
	#calculate average values for each pixel
	print("----- Averaging Images -----")
	os.chdir("./process/resized")
	
	for i in range(4):
		os.chdir("./tile"+str(i))
		
		allfiles = os.listdir()
		tilelist = [filename for filename in allfiles if filename[:7] == "aligned"] 
		N = len(tilelist)
		
		#Averaging 16bit Images
		if io.imread(tilelist[0]).dtype == "uint16":
			th, tw = io.imread(tilelist[0]).shape[:2]
			pooltile = np.zeros((th,tw,3), dtype=float)
			
			for j in range(N):
				print("Processing Tile " + str(j) + ": " + tilelist[j])
				tile = io.imread(tilelist[j])
				pooltile += tile/N
		
			pooltile = np.round(pooltile).astype(np.uint16)
			io.imsave("avg_tile" + str(i) + ".tif", tile)
		
		#Averaging 8bit Images
		if io.imread(tilelist[0]).dtype == "uint8":
			tw, th = Image.open(tilelist[0]).size
			pooltile = np.zeros((th,tw,3), dtype=float)
			
			for j in range(N):
				print("Processing Tile " + str(j) + ": " + tilelist[j])
				tile = np.array(Image.open(tilelist[j]))
				pooltile += tile/N
			
			pooltile = np.round(pooltile).astype(np.uint8)
			outpooltile = Image.fromarray(pooltile,mode="RGB")
			outpooltile.save("avg_tile" + str(i) + ".tif", format='TIFF', compression='None')
		os.chdir("..")

	os.chdir("../..")
		
def median():
	#Calculate Median of Images ------vips_extract_band ()
	print("----- Medianing Images -----")
	os.chdir("./process/resized")
	for i in range(4):
		os.chdir("./tile"+str(i))
		
		allfiles = os.listdir()
		tilelist = [filename for filename in allfiles if filename[:7] == "aligned"] 
		N = len(tilelist)
		
		#Median of 16bit Images
		if io.imread(tilelist[0]).dtype == "uint16":
			#get tile size
			th, tw = io.imread(tilelist[0]).shape[:2]
			
			#create arrays to hold all layers of a single color channel
			RGBmedian = np.zeros((th,tw,N), dtype=np.uint16)
			poolmedian = np.zeros((th,tw,3))
			
			for rgb in range(0,3):
				color = ["reds","greens","blues"]
				print("Processing median of " + color[rgb] + " Tile: " + str(i))
				
				for j in range(N):
					tile = io.imread(tilelist[j])
					#copies one color channel into an array containing the same channel from all tiles
					RGBmedian[:,:,j] = tile[:,:,rgb]
				poolmedian[:,:,rgb] = np.median(RGBmedian, axis=2, overwrite_input=True)
			
			poolmedian = np.round(poolmedian).astype(np.uint16)
			io.imsave("median_tile" + str(i) + ".tif", tile)
			
		#Median of 8bit Images
		if io.imread(tilelist[0]).dtype == "uint8":
			#get tile size
			tw, th = Image.open(tilelist[0]).size
			
			#create array to hold all layers of a single color channel
			RGBmedian = np.zeros((th,tw,N), dtype=np.uint8)
			poolmedian = np.zeros((th,tw,3))
			
			for rgb in range(0,3):
				color = ["reds","greens","blues"]
				print("Processing median of " + color[rgb] + " Tile: " + str(i))
				
				for j in range(N):
					tile = np.array(Image.open(tilelist[j]))
					#copies one color channel into an array containing the same channel from all tiles
					RGBmedian[:,:,j] = tile[:,:,rgb]
				poolmedian[:,:,rgb] = np.median(RGBmedian, axis=2, overwrite_input=True)
			
			poolmedian = np.round(poolmedian).astype(np.uint8)
			outpoolmedian = Image.fromarray(poolmedian,mode="RGB")
			outpoolmedian.save("median_tile" + str(i) + ".tif", format='TIFF', compression='None')
		os.chdir("..")

	os.chdir("../..")
		
def stitch():
	#Stitch all tiles back together
	print("----- Stitching Images -----")
	if not os.path.exists("./process/superresolution"):
		os.mkdir("./process/superresolution")
	os.chdir("./process/resized")
	
	#processed methods
	methods = ["avg", "median"]
	
	for m in methods:
		tile0 = pyvips.Image.new_from_file("./tile0/" + m + "_tile0.tif", access='sequential')
		tile1 = pyvips.Image.new_from_file("./tile1/" + m + "_tile1.tif", access='sequential')
		tile2 = pyvips.Image.new_from_file("./tile2/" + m + "_tile2.tif", access='sequential')
		tile3 = pyvips.Image.new_from_file("./tile3/" + m + "_tile3.tif", access='sequential')
		
		merged = pyvips.Image.arrayjoin([tile0,tile2,tile1,tile3], across=2)
		merged.write_to_file("../superresolution/" + m + "_result.tif")
	
	#remove merged tiles
	os.chdir("../..")
	os.system("rm -r ./process/resized")
	
if __name__ == '__main__':
	main()
