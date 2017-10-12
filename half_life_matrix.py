#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import argparse
import matrix_functions as mf
import sys
import h5py
import shutil

parser = argparse.ArgumentParser(description='Create half-life matrix from timecourse')
parser.add_argument('-i', help= 'timecourse hdf5 files in order Mock -> Overnight digestion',
		nargs=7)
args = parser.parse_args()

def check_shape(x):
	'''
	Check if dimensions of numpy arrays are equal

	Args: 
		x : list of numpy ndarrays
	Returns:
		bool: True if dimensions are equal,
		false otherwise		
	'''
	dim_1 = x[0].shape
	flag = True
	for m in x[1:]:
		if m.shape != dim_1:
			flag = False 
	return flag

def scatter_plot(i, t, xp, p, out, hl, pm):
	'''
	Plot a scatter_plot of interactions vs time

	Args:
		i: interactions from timecourse
		t: time in minutes
	'''
	fig, ax = plt.subplots(figsize=(8,4))
	# ax.spines['right'].set_visible(False)
	# ax.spines['top'].set_visible(False)
	# ax.spines['left'].set_linewidth(2)
	# ax.spines['bottom'].set_linewidth(2)
	# ax.yaxis.set_ticks_position('left')
	# ax.xaxis.set_ticks_position('bottom')
	# ax.xaxis.set_tick_params(width=2)
	# ax.yaxis.set_tick_params(width=2)
	ax.set_xlim([-10,1200])
	ax.set_ylim([-10,6500])
	ax.scatter(t, i)
	print type(i[0])
	print type(t[0])
	ax.plot(xp, p(xp))
	ax.vlines(hl, 0, 6000, colors='r')
	ax.hlines(pm, 0, 500, colors='r')
	plt.savefig(out, dpi=300)
	plt.close()
	return

def get_half_life(i, t):
	'''
	Get half life of interactions for 2D position in
	Hi-C matrix

	Args: 
		i: interactions from timecourse
		t: time in minutes
	Returns:
		hl: half-life in minutes 
	'''

	# Assign half-life to zero if interactions at 
	# 4 hours or overnight is greater than mock 
	if i[0] <= i[5] or i[0] <= i[6]:
		hl = 0
		predict_mid = 0
		return hl, predict_mid
	else:
		# Get half-life
		x = np.linspace(0, 1000, 2001)
		z = np.polyfit(t, i, 2)
		poly = np.poly1d(z)
		predict = poly(x)
		# For now using middle of interaction range per pixel
		# to determine half-life, get more sophisticated later
		mid = ((i[0] - i[6]) / 2.0 ) + i[6]
		idx = np.argmin(np.abs(predict - mid))
		hl = x[idx]
		predict_mid = predict[idx]
		return hl, predict_mid
	

	


def main():

	# Create copy of mock and use that to write over
	# with half life data
	shutil.copy(args.i[0], 'half_life_chr14.hdf5')
	f = h5py.File('half_life_chr14.hdf5', 'r+')

	# List of timecourse file objects in order
	f_obj_list = []
	for a in args.i:
		f_obj_list.append(h5py.File(a, 'r'))

	# List of chromosome 14 matrices for timecourse data
	# in order
	chr14_list = []
	for o in f_obj_list:
		chr14_list.append(mf.get_cis_matrix(o, 'chr14'))

	if not check_shape(chr14_list):
		print 'ERROR unequal dimensions for cis matrices'
		sys.exit()

	interactions = []
	time = np.array([0, 5, 60, 120, 180, 240, 960])
	for h in chr14_list:
		interactions.append(h[80, 90])
	

	# # polyfit
	# z = np.polyfit(time, interactions, 2)
	# p = np.poly1d(z)
	# print z
	# xp = np.linspace(-10, 1000, 100)
	# print xp
	# scatter_plot(interactions, time, xp, p, 'test_10.png')


	# interactions = []
	# for h in chr14_list:
	# 	interactions.append(h[80,180])

	# # polyfit
	# z = np.polyfit(time, interactions, 2)
	# p = np.poly1d(z)
	# xp = np.linspace(-10, 1000, 100)
	# scatter_plot(interactions, time, xp, p, 'test_100.png')
	# print interactions

	# interactions = []
	# for h in chr14_list:
	# 	interactions.append(h[80,85])

	# polyfit
	z = np.polyfit(time, interactions, 2)
	p = np.poly1d(z)
	xp = np.linspace(-10, 1000, 100)
	#scatter_plot(interactions, time, xp, p, 'test_5.png')
	#print interactions

	# interactions = []
	# for h in chr14_list:
	# 	interactions.append(h[80,120])

	# # polyfit
	# z = np.polyfit(time, interactions, 2)
	# p = np.poly1d(z)
	# xp = np.linspace(-10, 1000, 100)
	# scatter_plot(interactions, time, xp, p, 'test_40.png')

	hl, pred_mid = get_half_life(interactions, time)
	print '*****hl*****'
	print hl
	print '************'	

	#scatter_plot(interactions, time, xp, p, 'test_10_lines.png', hl, pred_mid)
	chrom = 'chr14'
	chr_idx, = np.where(f['chrs'][:] == chrom)
	chr_idx = chr_idx[0]
	bins = f['chr_bin_range'][chr_idx]
	print bins
	print len(range(bins[0], bins[1] + 1))
	
	print f['interactions'][bins[0] + 80, bins[0] + 90]
	for i in range((bins[1] - bins[0]) + 1):
		print 'on row: ' + str(i)
		for j in range((bins[1] - bins[0]) + 1):
			interactions = []
			for h in chr14_list:
				interactions.append(h[i, j])
			hl, pred_mid = get_half_life(interactions, time)
			f['interactions'][bins[0] + i, bins[0] + j] = hl
	print f['interactions'][:]
	print f['interactions'][bins[0] + 80, bins[0] + 90]

	f.close()




if __name__ == '__main__':
	main()


