import os
import numpy as np
from PIL import Image

def main():
	#resize images to 200%
	resize()
	#call hugin to do analignment, crop to common covered area
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

def align():
	os.chdir("./resized")
	os.system("align_image_stack --use-given-order -C -x -y -z -a aligned_ --corr=0.8 -t 1 -c 100 -v --gpu *.tif")
	os.system("rm *_resized.tif")

def resize():
	os.chdir("./process")
	try:
		os.mkdir("./resized")
	except:
		print("dir present")
		
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	N = len(imlist)
	
	for i in range(N):
		print("Resizing: " + imlist[i])
		npimage = np.array(Image.open(imlist[i]))
		h, w = npimage.shape[:2]
		out = Image.fromarray(npimage,mode="RGB")
		out = out.resize((w*2,h*2), Image.BILINEAR) #LANCZOS BILINEAR NEAREST
		out.save("./resized/" + imlist[i][:-4] + "_resized.tif", format='TIFF', compression='None') #tiff_lzw

def stitch():
	print("Stitching everything together")
	os.mkdir("../superresolution")
	
	#stitch average
	tile1 = Image.open("./tile1/avg_tile1.tif")
	tile2 = Image.open("./tile2/avg_tile2.tif")
	tile3 = Image.open("./tile3/avg_tile3.tif")
	tile4 = Image.open("./tile4/avg_tile4.tif")
	
	w1, h1 = tile1.size
	w2, h2 = tile2.size
	w3, h3 = tile3.size
	
	merged = Image.new('RGB', (w1 + w3, h1 + h2))
	merged.paste(im = tile1, box=(0,0))
	merged.paste(im = tile2, box=(0,h1))
	merged.paste(im = tile3, box=(w1,0))
	merged.paste(im = tile4, box=(w1,h1))
	
	merged.save("../superresolution/avg_result.tif", format='TIFF', compression='None')

	#stitch median
	tile1 = Image.open("./tile1/median_tile1.tif")
	tile2 = Image.open("./tile2/median_tile2.tif")
	tile3 = Image.open("./tile3/median_tile3.tif")
	tile4 = Image.open("./tile4/median_tile4.tif")
	
	w1, h1 = tile1.size
	w2, h2 = tile2.size
	w3, h3 = tile3.size
	
	merged = Image.new('RGB', (w1 + w3, h1 + h2))
	merged.paste(im = tile1, box=(0,0))
	merged.paste(im = tile2, box=(0,h1))
	merged.paste(im = tile3, box=(w1,0))
	merged.paste(im = tile4, box=(w1,h1))
	
	merged.save("../superresolution/median_result.tif", format='TIFF', compression='None')
	
	#remove merged images
	os.system("rm -r ../resized")
	
def average():
	print("making averages")
	for i in range(1,5):
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

def median():
	print("making medians")
	for i in range(1,5):
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
			print("Processing median of color Channel: " + str(rgb) + " Tile: " + str(i))
			for j in range(N):
				tile = np.array(Image.open(tilelist[j]))
				RGBmedian[:,:,j] = tile[:,:,rgb]
			poolmedian[:,:,rgb] = np.median(RGBmedian, axis=2, overwrite_input=True)
		
		poolmedian = np.array(np.rint(poolmedian),dtype=np.uint8)
		outpoolmedian = Image.fromarray(poolmedian,mode="RGB")
		outpoolmedian.save("median_tile" + str(i) + ".tif", format='TIFF', compression='None')
		os.chdir("..")
	
def tile():
	#create folders for the tiles
	for i in range(1,5):
		try:
			os.mkdir("tile"+str(i))
		except:
			print("folder present")
	#get list of image files
	allfiles = os.listdir()
	imlist = [filename for filename in allfiles if filename[-4:] in [".jpg",".JPG",".tif",".TIF","TIFF","tiff"]]
	
	# load images and split into 4 tiles
	width, height = Image.open(imlist[0]).size
	N = len(imlist)
	for i in range(N):
		print("Tiling: " + imlist[i])
		npimage = np.array(Image.open(imlist[i]))
		
		#delete alpha channel -> tif
		if npimage.shape[2] == 4:
			npimage = np.delete(npimage,3,2)
		
		#make boundaries for four tiles
		tdimw = int(width/2)
		tdimh = int(height/2)
		tile1 = npimage[:tdimh,:tdimw,:]
		tile2 = npimage[tdimh:,:tdimw,:]
		tile3 = npimage[:tdimh,tdimw:,:]
		tile4 = npimage[tdimh:,tdimw:,:]
		
		#save and resize tiles
		outtile1 = Image.fromarray(tile1,mode="RGB")
		outtile1.save("./tile1/" + imlist[i][:-4] + "_tile1.tif", format='TIFF', compression='None')
		
		outtile2 = Image.fromarray(tile2,mode="RGB")
		outtile2.save("./tile2/" + imlist[i][:-4] + "_tile2.tif", format='TIFF', compression='None')

		outtile3 = Image.fromarray(tile3,mode="RGB")
		outtile3.save("./tile3/" + imlist[i][:-4] + "_tile3.tif", format='TIFF', compression='None')

		outtile4 = Image.fromarray(tile4,mode="RGB")
		outtile4.save("./tile4/" + imlist[i][:-4] + "_tile4.tif", format='TIFF', compression='None')
	
	#remove aligned images
	os.system("rm align*")
	
if __name__ == '__main__':
	main()
