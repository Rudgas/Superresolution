#!/usr/bin/env python3

import os
import numpy as np
from PIL import Image

def main():
	### setup ###
	
	
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
	try:
		os.chdir("./process")
	except:
		print("Please create a folder 'process' and add images that are to be processed")
		exit()
	try:
		os.mkdir("./resized")
	except:
		print("Directory already created")
	
	#get a list of all files
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	N = len(imlist)
	
	#resize the images, different algorithms areavailable
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
	os.chdir("./process/resized")
	os.system("align_image_stack --use-given-order -C -x -y -z -a aligned_ --corr=0.8 -t 1 -c 100 -v --gpu *.tif")
	os.system("rm *_resized.tif")
	os.chdir("../..")

def tile():
	os.chdir("./process/resized")
	#create folders for the 4 tiles
	for i in range(4):
		try:
			os.mkdir("tile"+str(i))
		except:
			print("folder present")
	#get list of image files
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	
	#load images and split into 4 tiles
	width, height = Image.open(imlist[0]).size
	N = len(imlist)
	for i in range(N):
		print("Tiling: " + imlist[i])
		npimage = np.array(Image.open(imlist[i]))
		
		#delete alpha channel -> tif
		if npimage.shape[2] == 4:
			npimage = np.delete(npimage,3,2)
		
		#calculate boundaries for four tiles
		tdimw = int(width/2)
		tdimh = int(height/2)
		
		tile0 = npimage[:tdimh,:tdimw,:]
		tile1 = npimage[tdimh:,:tdimw,:]
		tile2 = npimage[:tdimh,tdimw:,:]
		tile3 = npimage[tdimh:,tdimw:,:]
		
		outtile = Image.fromarray(tile0,mode="RGB")
		outtile.save("./tile0/" + imlist[i][:-4] + "_tile0.tif", format='TIFF', compression='None')
		outtile = Image.fromarray(tile1,mode="RGB")
		outtile.save("./tile1/" + imlist[i][:-4] + "_tile1.tif", format='TIFF', compression='None')
		outtile = Image.fromarray(tile2,mode="RGB")
		outtile.save("./tile2/" + imlist[i][:-4] + "_tile2.tif", format='TIFF', compression='None')
		outtile = Image.fromarray(tile3,mode="RGB")
		outtile.save("./tile3/" + imlist[i][:-4] + "_tile3.tif", format='TIFF', compression='None')

		# ~ tile = np.zeros((tdimh,tdimw,3,4),dtype=np.uint8)
		
		# ~ tile[:,:,:,0] = npimage[:tdimh,:tdimw,:]
		# ~ tile[:,:,:,1] = npimage[tdimh:,:tdimw,:]
		# ~ tile[:,:,:,2] = npimage[:tdimh,tdimw:,:]
		# ~ tile[:,:,:,3] = npimage[tdimh:,tdimw:,:]
		
		# ~ for j in range(0,4):
			# ~ outtile = Image.fromarray(tile[:,:,:,j],mode="RGB")
			# ~ outtile.save("./tile" + str(j) + "/" + imlist[i][:-4] + "_tile" + str(j) + ".tif", format='TIFF', compression='None')
		
		
		
	#remove aligned images
	os.system("rm align*")
	os.chdir("../..")
	
def average():
	#calculate average values for each pixel
	os.chdir("./process/resized")
	print("Calculating averages")
	for i in range(4):
		os.chdir("./tile"+str(i))
		
		allfiles = os.listdir()
		tilelist = [filename for filename in allfiles if filename[:5] == "align"] 
		N = len(tilelist)
		
		tw, th = Image.open(tilelist[0]).size
		pooltile = np.zeros((th,tw,3), dtype=float)
		
		for j in range(N):
			print("Processing Tile " + str(i) + ": " + tilelist[j])
			tile = np.array(Image.open(tilelist[j]))
			pooltile += tile/N
		pooltile = np.array(np.round(pooltile),dtype=np.uint8)
		outpooltile = Image.fromarray(pooltile,mode="RGB")
		outpooltile.save("avg_tile" + str(i) + ".tif", format='TIFF', compression='None')
		os.chdir("..")
	os.chdir("../..")
		
def median():
	os.chdir("./process/resized")
	print("Calculating median values")
	for i in range(4):
		os.chdir("./tile"+str(i))
		
		allfiles = os.listdir()
		tilelist = [filename for filename in allfiles if filename[:5] == "align"] 
		N = len(tilelist)
		
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
		
		poolmedian = np.array(np.rint(poolmedian),dtype=np.uint8)
		outpoolmedian = Image.fromarray(poolmedian,mode="RGB")
		outpoolmedian.save("median_tile" + str(i) + ".tif", format='TIFF', compression='None')
		os.chdir("..")
	os.chdir("../..")
		
def stitch():
	try: 
		os.mkdir("./process/superresolution")
	except:
		print("folder present")
	os.chdir("./process/resized")
	print("Stitching everything together")
	
	#combination
	methods = ["avg", "median"]
	
	for i in methods:
		#load tiles
		tile0 = Image.open("./tile0/" + i + "_tile0.tif")
		tile1 = Image.open("./tile1/" + i + "_tile1.tif")
		tile2 = Image.open("./tile2/" + i + "_tile2.tif")
		tile3 = Image.open("./tile3/" + i + "_tile3.tif")
		
		#in case the original has an uneven number of pixels along an axis, we use all three tiles
		w1, h1 = tile0.size
		w2, h2 = tile1.size
		w3, h3 = tile2.size
		
		#create merged image
		merged = Image.new('RGB', (w1 + w3, h1 + h2))
		merged.paste(im = tile0, box=(0,0))
		merged.paste(im = tile1, box=(0,h1))
		merged.paste(im = tile2, box=(w1,0))
		merged.paste(im = tile3, box=(w1,h1))
		
		merged.save("../superresolution/" + i + "_result.tif", format='TIFF', compression='None')

	#remove merged tiles
	os.chdir("../..")
	os.system("rm -r ./process/resized")
	
if __name__ == '__main__':
	main()
