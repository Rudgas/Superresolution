#!/usr/bin/env python3

import os
import numpy as np
from skimage import io, transform
from PIL import Image

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
	
	#For 16bit Images: split images into 4 before resizing, however
	#this eliminiates using any extrapolation for the upscaling as
	#it would produce seams in the final image
	if io.imread(imlist[0]).dtype == "uint16":
		h, w = io.imread(imlist[0]).shape[:2]
		ht = int(h/2)
		wt = int(w/2)
		for i in range(N):
			print("Resizing: " + imlist[i])
		
			image = io.imread(imlist[i])
			
			tile = image[:ht,:wt]
			tile = transform.resize(tile,(ht*2,wt*2),order=0,preserve_range=True, mode='edge', anti_aliasing=True) #0 Nearest neighbor 1 Biliniear 2 Biquadratic 3 Bicubic 4 Biquartic 5 biquintic
			tile = np.round(tile).astype(np.uint16)
			io.imsave("./resized/" + imlist[i][:-4] + "_resized_tile0.tif", tile)
			h0, w0 = tile.shape[:2]
			
			tile = image[ht:,:wt]
			tile = transform.resize(tile,(ht*2,wt*2),order=0,preserve_range=True, mode='edge', anti_aliasing=True) #0 Nearest neighbor 1 Biliniear 2 Biquadratic 3 Bicubic 4 Biquartic 5 biquintic
			tile = np.round(tile).astype(np.uint16)
			io.imsave("./resized/" + imlist[i][:-4] + "_resized_tile1.tif", tile)			
			
			tile = image[:ht,wt:]
			tile = transform.resize(tile,(ht*2,wt*2),order=0,preserve_range=True, mode='edge', anti_aliasing=True) #0 Nearest neighbor 1 Biliniear 2 Biquadratic 3 Bicubic 4 Biquartic 5 biquintic
			tile = np.round(tile).astype(np.uint16)
			io.imsave("./resized/" + imlist[i][:-4] + "_resized_tile2.tif", tile)			
			
			tile = image[ht:,wt:]
			tile = transform.resize(tile,(ht*2,wt*2),order=0,preserve_range=True, mode='edge', anti_aliasing=True) #0 Nearest neighbor 1 Biliniear 2 Biquadratic 3 Bicubic 4 Biquartic 5 biquintic
			tile = np.round(tile).astype(np.uint16)
			h3, w3 = tile.shape[:2]
			
			merged = np.zeros((h0+h3,w0+w3,3), dtype=np.uint16)
			
			merged[h0:,w0:,:] = tile
			merged[:h0,:w0,:] = io.imread("./resized/" + imlist[i][:-4] + "_resized_tile0.tif")
			merged[h0:,:w0,:] = io.imread("./resized/" + imlist[i][:-4] + "_resized_tile1.tif")
			merged[:h0,w0:,:] = io.imread("./resized/" + imlist[i][:-4] + "_resized_tile2.tif")
			
			io.imsave("./resized/" + imlist[i][:-4] + "_resized.tif", merged)
			os.system("rm ./resized/*tile*")
		
	#Use Pillow instead of skimage for 8bit images as skimage converts to float64 when rescaling				
	if io.imread(imlist[0]).dtype == "uint8":
		for i in range(N):
			print("Resizing: " + imlist[i])
			npimage = np.array(Image.open(imlist[i]))
			h, w = npimage.shape[:2]
			out = Image.fromarray(npimage,mode="RGB")
			out = out.resize((w*2,h*2), Image.BILINEAR) #Alternatives: Image.LANCZOS Image.BILINEAR Image.NEAREST
			out.save("./resized/" + imlist[i][:-4] + "_resized.tif", format='TIFF', compression='None') #tiff_lzw

	#return to parent directory
	os.chdir("..")

def align():
	#use hugin for alignment of images
	print("----- Aligning Images -----")
	os.chdir("./process/resized")
	os.system("align_image_stack --use-given-order -C -x -y -z -a aligned_ --corr=0.8 -t 1 -c 100 -v --gpu *.tif")
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
	
	#Tiling 16 bit images
	if io.imread(imlist[0]).dtype == "uint16":
		for i in range(N):
			print("Tiling: " + imlist[i])
			image = io.imread(imlist[i])
			
			#it is much faster to recalculate height and width inside the loop rather than loading an image outside
			h, w = image.shape[:2]
			ht = int(h/2)
			wt = int(w/2)
			
			#remove alpha channel
			if image.shape[2] == 4:
				image = np.delete(image,3,2)
			
			#save tiles
			tile = image[:ht,:wt]
			io.imsave("./tile0/" + imlist[i][:-4] + "_tile0.tif", tile)		
			tile = image[ht:,:wt]
			io.imsave("./tile1/" + imlist[i][:-4] + "_tile1.tif", tile)			
			tile = image[:ht,wt:]
			io.imsave("./tile2/" + imlist[i][:-4] + "_tile2.tif", tile)			
			tile = image[ht:,wt:]
			io.imsave("./tile3/" + imlist[i][:-4] + "_tile3.tif", tile)
			
	#Tiling 8bit images
	if io.imread(imlist[0]).dtype == "uint8":
		#load images and split into 4 tiles
		for i in range(N):
			print("Tiling: " + imlist[i])
			
			npimage = np.array(Image.open(imlist[i]))
			width, height = npimage.shape[:2]
			
			#calculate boundaries for four tiles
			tdimw = int(width/2)
			tdimh = int(height/2)
			
			#delete alpha channel -> tif
			if npimage.shape[2] == 4:
				npimage = np.delete(npimage,3,2)
			
			tile = npimage[:tdimh,:tdimw,:]
			tile = Image.fromarray(tile,mode="RGB")
			tile.save("./tile0/" + imlist[i][:-4] + "_tile0.tif", format='TIFF', compression='None')
			tile = npimage[tdimh:,:tdimw,:]
			tile = Image.fromarray(tile,mode="RGB")
			tile.save("./tile1/" + imlist[i][:-4] + "_tile1.tif", format='TIFF', compression='None')
			tile = npimage[:tdimh,tdimw:,:]
			tile = Image.fromarray(tile,mode="RGB")
			tile.save("./tile2/" + imlist[i][:-4] + "_tile2.tif", format='TIFF', compression='None')
			tile = npimage[tdimh:,tdimw:,:]
			tile = Image.fromarray(tile,mode="RGB")
			tile.save("./tile3/" + imlist[i][:-4] + "_tile3.tif", format='TIFF', compression='None')
			
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
	#Calculate Median of Images
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
	
	#combination
	methods = ["avg", "median"]
	
	for m in methods:
		
		#Stitching of 16bit Images
		if io.imread("./tile0/" + m + "_tile0.tif").dtype == "uint16":
			#load images to asses dimensions
			h3, w3 = io.imread("./tile3/" + m + "_tile3.tif").shape[:2]
			tile = io.imread("./tile0/" + m + "_tile0.tif")
			h0, w0 = tile.shape[:2]
			
			#create canvas
			merged = np.zeros((h0+h3,w0+w3,3), dtype=np.uint16)
			
			#add all tiles
			merged[:h0,:w0,:] = tile
			merged[h0:,:w0,:] = io.imread("./tile1/" + m + "_tile1.tif")
			merged[:h0,w0:,:] = io.imread("./tile2/" + m + "_tile2.tif")
			merged[h0:,w0:,:] = io.imread("./tile3/" + m + "_tile3.tif")
			
			io.imsave("../superresolution/" + m + "_result.tif", merged)
			
		#Stitching of 8bit Images
		if io.imread("./tile0/" + m + "_tile0.tif").dtype == "uint8":
			#load images to asses dimensions
			w3, h3 = Image.open("./tile3/" + m + "_tile3.tif").size
			tile = Image.open("./tile0/" + m + "_tile0.tif")
			w0, h0 = tile.size
			
			#create canvas
			merged = Image.new('RGB', (w0 + w3, h0 + h3))
			
			#add all tiles
			merged.paste(im = tile, box=(0,0))
			tile = Image.open("./tile1/" + m + "_tile1.tif")
			merged.paste(im = tile, box=(0,h0))
			tile = Image.open("./tile2/" + m + "_tile2.tif")
			merged.paste(im = tile, box=(w0,0))
			tile = Image.open("./tile3/" + m + "_tile3.tif")
			merged.paste(im = tile, box=(w0,h0))
			
			merged.save("../superresolution/" + m + "_result.tif", format='TIFF', compression='None')

	#remove merged tiles
	os.chdir("../..")
	os.system("rm -r ./process/resized")
	
if __name__ == '__main__':
	main()
