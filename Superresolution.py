#!/usr/bin/env python3

import os
import pyvips

def main():
	### setup ###
	#configure extrapolation methods in the future
	
	#resize images to 200%
	resize()
	
	#call hugin to do an alignment, crop to common covered area
	align()
	
	#calculate average for each pixel
	average()
	
	#calculate median for each pixel
	median()
	
	#remove intermediary files
	cleanup()
	
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
		img = pyvips.Image.new_from_file(imlist[i], access='sequential')
		#img = img.gaussblur(0.45, precision='float', min_ampl=0.01).cast('uchar')
		#img = img.gaussblur(0.50, precision='float', min_ampl=0.01).cast('uchar')
		out = img.resize(2, kernel = "linear", centre = True) #nearest linear cubic mitchell lanczos2 lanczos3
		out.write_to_file("./resized/" + imlist[i][:-4] + "_resized.tif")
		
	#return to parent directory
	os.chdir("..")
	
def align():
	print("----- Aligning Images -----")
	#use hugin for alignment of images
	os.chdir("./process/resized")
	os.system("align_image_stack --use-given-order -C -x -y -z -a aligned_ -s 1 --corr=0.8 -t 1 -c 100 -v --gpu *.tif") #try scale option
	os.system("rm *_resized.tif")
	os.chdir("../..")
	
def average():
	#calculate average values for each pixel
	print("----- Averaging Images -----")
	os.chdir("./process/resized")
	
	allfiles = os.listdir()
	tilelist = [filename for filename in allfiles if filename[:7] == "aligned"] 
	N = len(tilelist)
	
	#get dtpye of input data
	avgs = pyvips.Image.new_from_file(tilelist[0], access='sequential')
	input_format = avgs.format
	
	#make list containing all images	
	avgs = []
	for i in range(N):
		avgs.append(pyvips.Image.new_from_file(tilelist[i], access='sequential'))
	
	#calculate average: round and cast to former datatype
	avg = pyvips.Image.sum(avgs)/N
	avg = avg.rint()
	avg = avg.cast(input_format)
	
	#check if folder available
	if not os.path.exists("../superresolution"):
		os.mkdir("../superresolution")
	
	avg.write_to_file("../superresolution/avg_result.tif")
	
	os.chdir("../..")	
	
def median():
	#Calculate Median of Images ------vips_extract_band ()
	print("----- Medianing Images -----")
	os.chdir("./process/resized")
	
	allfiles = os.listdir()
	tilelist = [filename for filename in allfiles if filename[:7] == "aligned"] 
	N = len(tilelist)
	
	reds = []
	greens = []
	blues = []
	
	#extract each color
	for j in range(N):
		reds.append(pyvips.Image.new_from_file(tilelist[j], access='sequential')[0])
		greens.append(pyvips.Image.new_from_file(tilelist[j], access='sequential')[1])
		blues.append(pyvips.Image.new_from_file(tilelist[j], access='sequential')[2])
	
	#find median for each channel
	red = pyvips.Image.bandrank(N, reds)
	green = pyvips.Image.bandrank(N, greens)
	blue = pyvips.Image.bandrank(N, blues)
	
	#join rgb bands again
	median = red.bandjoin(green)
	median = median.bandjoin(blue)
	
	#check if folder available
	if not os.path.exists("../superresolution"):
		os.mkdir("../superresolution")
	
	median.write_to_file("../superresolution/median_result.tif")
		
	os.chdir("../..")		
		
def cleanup():
	os.system("rm -r ./process/resized")
	
if __name__ == '__main__':
	main()
