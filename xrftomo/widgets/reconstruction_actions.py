# #########################################################################
# Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2018. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENTn SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import xrftomo
import tomopy
import os
from matplotlib.pyplot import *
import numpy as np


class ReconstructionActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')
	fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

	def __init__(self):
		super(ReconstructionActions, self).__init__()

	def reconstruct(self, data, element, center, method, beta, delta, iters, thetas, show_stats=False):
		'''
		load data for reconstruction and load variables for reconstruction
		make it sure that data doesn't have infinity or nan as one of
		entries
		'''
		recData = data[element, :, :, :]
		recData[recData == np.inf] = True
		recData[np.isnan(recData)] = True
		recCenter = np.array(center, dtype=np.float32)

		print("working fine")

		if method == 0:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180, 
				algorithm='mlem', center=recCenter, num_iter=iters, accelerated=True, device='cpu')
		elif method == 1:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180,
				algorithm='gridrec')
		elif method == 2:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180, 
				algorithm='art', num_iter=iters)
		elif method == 3:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180, 
				algorithm='pml_hybrid', center=recCenter, 
				reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)
		elif method == 4:
			self.recon = tomopy.recon(recData, thetas * np.pi / 180,
				algorithm='pml_quad', center=recCenter,
				reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)
		elif method == 5:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180,
				algorithm='fbp')
		elif method == 6:
			self.recon= tomopy.recon(recData, thetas * np.pi / 180, 
				algorithm='sirt', num_iter=iters)
		elif method == 7:
			self.recon = tomopy.recon(recData, thetas * np.pi / 180,
				algorithm='tv', center=recCenter,
				reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)

		#tomopy.remove_nan() does not remove inf values
		self.recon = tomopy.remove_nan(self.recon)

		if np.isinf(self.recon).max():
			print("WARNING: inf values found in reconstruction, consider reconstructing with less iterations")
			print("inf values replaced with 0.001")
			self.recon[self.recon == np.inf] = 0.001

		err, mse  = self.assessRecon(self.recon, data, thetas, show_stats)
		print(mse)
		return self.recon

	def reconstructAll(self, data, element_names, center, method, beta, delta, iters, thetas):
		print("This will take a while")
		save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
		num_elements = data.shape[0]
		for i in range(num_elements):
			print("running reconstruction for:", element_names[i])
			recon = self.reconstruct(data, i, center, method, beta, delta, iters, thetas)
			savepath = save_path+'/'+element_names[i]
			savedir = savepath+'/'+element_names[i]
			os.makedirs(savepath)
			xrftomo.SaveOptions.save_reconstruction(self, recon, savedir)

		return recon

	def assessRecon(self,recon, data, thetas, show_plots=True):
		#get index where projection angle is zero
		zero_index = np.where(abs(thetas)==abs(thetas).min())[0][0]
		num_slices = recon.shape[0]
		width = self.recon.shape[1]
		reprojection = np.zeros([num_slices, width])
		tmp = np.zeros([num_slices, width])

		# get recon reporjection for slice i and take the difference with data projection (at angle ~=0).
		for i in range(num_slices):
			reprojection[i] = np.sum(recon[i], axis=0)
			tmp[i] = data[0, zero_index, i] / (data[0, zero_index, i].max() / np.sum(recon[i], axis=0).max())
		tmp = tmp/(tmp.max()/width)
		reprojection = reprojection/(reprojection.max()/width)
		#difference between reporjection and original projection at angle == 0
		# err = tmp - reprojection/reprojection
		err = tmp - reprojection
		#mean squared error
		mse = (np.square(err)).mean(axis=None)
		imshow(recon[num_slices//2], origin='lower'), plot(tmp[num_slices//2]), plot(reprojection[num_slices//2])
		legend((' original data', 'reprojection'), loc=1)
		title("MSE:{}".format(np.round(mse, 4)))
		if show_plots:
			show()
		return err, mse

	def reconMultiply(self):
		'''
		multiply reconstruction by 10
		'''
		self.recon = self.recon * 10
		return self.recon
	def reconDivide(self, recon):
		'''
		divide reconstuction by 10
		'''
		self.recon = recon / 10
		return self.recon
