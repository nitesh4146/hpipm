###################################################################################################
#                                                                                                 #
# This file is part of HPIPM.                                                                     #
#                                                                                                 #
# HPIPM -- High-Performance Interior Point Method.                                                #
# Copyright (C) 2019 by Gianluca Frison.                                                          #
# Developed at IMTEK (University of Freiburg) under the supervision of Moritz Diehl.              #
# All rights reserved.                                                                            #
#                                                                                                 #
# The 2-Clause BSD License                                                                        #
#                                                                                                 #
# Redistribution and use in source and binary forms, with or without                              #
# modification, are permitted provided that the following conditions are met:                     #
#                                                                                                 #
# 1. Redistributions of source code must retain the above copyright notice, this                  #
#    list of conditions and the following disclaimer.                                             #
# 2. Redistributions in binary form must reproduce the above copyright notice,                    #
#    this list of conditions and the following disclaimer in the documentation                    #
#    and/or other materials provided with the distribution.                                       #
#                                                                                                 #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND                 #
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED                   #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE                          #
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR                 #
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES                  #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;                    #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND                     #
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT                      #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS                   #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                    #
#                                                                                                 #
# Author: Gianluca Frison, gianluca.frison (at) imtek.uni-freiburg.de                             #
#                                                                                                 #
###################################################################################################
from ctypes import *
import ctypes.util 
import numpy as np
#import faulthandler

#faulthandler.enable()



class hpipm_ocp_qp:
	def __init__(self, dim):

		# save dim internally
		self.dim = dim

		# extract dim
		N = dim.N
		nx = dim.nx
		nu = dim.nu
		nbx = dim.nbx
		nbu = dim.nbu
		ng = dim.ng
		ns = dim.ns

		# local qp memory
		self.A = []
		for i in range(N):
			self.A.append(np.zeros((nx[i+1], nx[i])))

		self.B = []
		for i in range(N):
			self.B.append(np.zeros((nx[i+1], nu[i])))

		self.b = []
		for i in range(N):
			self.b.append(np.zeros((nx[i+1], 1)))

		self.Q = []
		for i in range(N+1):
			self.Q.append(np.zeros((nx[i], nx[i])))

		self.R = []
		for i in range(N+1):
			self.R.append(np.zeros((nu[i], nu[i])))

		self.S = []
		for i in range(N+1):
			self.S.append(np.zeros((nu[i], nx[i])))

		self.q = []
		for i in range(N+1):
			self.q.append(np.zeros((nx[i], 1)))

		self.r = []
		for i in range(N+1):
			self.r.append(np.zeros((nu[i], 1)))

		self.Jx = []
		for i in range(N+1):
			self.Jx.append(np.zeros((nbx[i], nx[i])))

		self.lx = []
		for i in range(N+1):
			self.lx.append(np.zeros((nbx[i], 1)))

		self.ux = []
		for i in range(N+1):
			self.ux.append(np.zeros((nbx[i], 1)))

		self.Ju = []
		for i in range(N+1):
			self.Ju.append(np.zeros((nbu[i], nu[i])))

		self.lu = []
		for i in range(N+1):
			self.lu.append(np.zeros((nbu[i], 1)))

		self.uu = []
		for i in range(N+1):
			self.uu.append(np.zeros((nbu[i], 1)))

		self.idxb = []
		for i in range(N+1):
			self.idxb.append(np.zeros((nbx[i]+nbu[i], 1), dtype=np.int32))

		self.lb = []
		for i in range(N+1):
			self.lb.append(np.zeros((nbu[i]+nbx[i], 1)))

		self.ub = []
		for i in range(N+1):
			self.ub.append(np.zeros((nbu[i]+nbx[i], 1)))

		self.C = []
		for i in range(N+1):
			self.C.append(np.zeros((ng[i], nx[i])))

		self.D = []
		for i in range(N+1):
			self.D.append(np.zeros((ng[i], nu[i])))

		self.lg = []
		for i in range(N+1):
			self.lg.append(np.zeros((ng[i], 1)))

		self.ug = []
		for i in range(N+1):
			self.ug.append(np.zeros((ng[i], 1)))

		self.Zl = []
		for i in range(N+1):
			self.Zl.append(np.zeros((ns[i], 1)))

		self.Zu = []
		for i in range(N+1):
			self.Zu.append(np.zeros((ns[i], 1)))

		self.zl = []
		for i in range(N+1):
			self.zl.append(np.zeros((ns[i], 1)))

		self.zu = []
		for i in range(N+1):
			self.zu.append(np.zeros((ns[i], 1)))

		self.lls = []
		for i in range(N+1):
			self.lls.append(np.zeros((ns[i], 1)))

		self.lus = []
		for i in range(N+1):
			self.lus.append(np.zeros((ns[i], 1)))

		self.Jsu = []
		for i in range(N+1):
			self.Jsu.append(np.zeros((nbu[i], ns[i])))

		self.Jsx = []
		for i in range(N+1):
			self.Jsx.append(np.zeros((nbx[i], ns[i])))

		self.Jsg = []
		for i in range(N+1):
			self.Jsg.append(np.zeros((ng[i], ns[i])))

		self.idxs = []
		for i in range(N+1):
			self.idxs.append(np.zeros((ns[i], 1), dtype=np.int32))

		# load hpipm shared library
		__hpipm   = CDLL('libhpipm.so')
		self.__hpipm = __hpipm

		# C qp struct
		qp_struct_size = __hpipm.d_ocp_qp_strsize()
		qp_struct = cast(create_string_buffer(qp_struct_size), c_void_p)
		self.qp_struct = qp_struct

		# C qp internal memory
		qp_mem_size = __hpipm.d_ocp_qp_memsize(dim.dim_struct)
		qp_mem = cast(create_string_buffer(qp_mem_size), c_void_p)
		self.qp_mem = qp_mem

		# create C qp
		__hpipm.d_ocp_qp_create(dim.dim_struct, qp_struct, qp_mem)


	
	def set(self, field, value, idx_start, idx_end=None):
		# cast to np array
		if type(value) is not np.ndarray:
			if (type(value) is int) or (type(value) is float):
				value_ = value
				value = np.array((1,))
				value[0] = value_

		# reshape np arrays with empty shape, that occur when using hpipm_matlab
		if type(value) is np.ndarray and value.shape == ():
			value_ = value
			value = np.array((1,))
			value[0] = value_

		nx  = self.dim.nx
		nu  = self.dim.nu
		nbx = self.dim.nbx
		nbu = self.dim.nbu
		ng  = self.dim.ng
		ns  = self.dim.ns

		dim_dict = {
			'A':   [nx,  1, nx, 0],
			'B':   [nx,  1, nu, 0], 
			'Q':   [nx,  0, nx, 0],
			'R':   [nu,  0, nu, 0], 
			'S':   [nx,  0, nu, 0],
			'C':   [ng,  0, nx, 0],
			'D':   [ng,  0, nu, 0], 
			'b':   [nx,  1, 1,  0],
			'q':   [nx,  0, 1,  0],
			'r':   [nu,  0, 1,  0],
			'lg':  [ng,  0, 1,  0],
			'ug':  [ng,  0, 1,  0],
			'Zl':  [ns,  0, ns, 0],
			'Zu':  [ns,  0, ns, 0], 
			'zl':  [ns,  0, 1,  0],
			'zu':  [ns,  0, 1,  0], 
			'lls': [ns,  0, 1,  0],
			'llu': [ns,  0, 1,  0], 
			'Jx':  [nbx, 0, nx, 0], 
			'lx':  [nbx, 0, 1,  0], 
			'ux':  [nbx, 0, 1,  0], 
			'Ju':  [nbu, 0, nu, 0], 
			'lu':  [nbu, 0, 1,  0], 
			'uu':  [nbu, 0, 1,  0], 
			'Jsu': [nbu, 0, ns, 0], 
			'Jsx': [nbx, 0, ns, 0], 
			'Jsg': [ng,  0, ns, 0], 
			}

		field_ = getattr(self, field)
		reshape_tuple = dim_dict[field]
		if idx_end==None:
			if hasattr(reshape_tuple[2], '__getitem__'):
				reshape_dim = (reshape_tuple[0][idx_start + reshape_tuple[1]], reshape_tuple[2][idx_start + reshape_tuple[3]])
			else:
				reshape_dim = (reshape_tuple[0][idx_start + reshape_tuple[1]], reshape_tuple[2])
			field_[idx_start] = value
			field_[idx_start] = field_[idx_start].reshape(reshape_dim)
			field_[idx_start] = field_[idx_start].transpose()
			field_[idx_start] = np.ascontiguousarray(field_[idx_start], dtype=np.float64)
			tmp = cast(field_[idx_start].ctypes.data, POINTER(c_double))
			field_name_b = field.encode('utf-8')
			self.__hpipm.d_ocp_qp_set(c_char_p(field_name_b), idx_start, tmp, self.qp_struct)
		else:
			for i in range(idx_start, idx_end+1):
				if hasattr(reshape_tuple[2], '__getitem__'):
					reshape_dim = (reshape_tuple[0][i + reshape_tuple[1]], reshape_tuple[2][i + reshape_tuple[3]])
				else:
					reshape_dim = (reshape_tuple[0][i + reshape_tuple[1]], reshape_tuple[2])
				field_[i] = value
				field_[i] = field_[i].reshape(reshape_dim)
				field_[i] = field_[i].transpose()
				field_[i] = np.ascontiguousarray(field_[i], dtype=np.float64)
				tmp = cast(field_[i].ctypes.data, POINTER(c_double))
				field_name_b = field.encode('utf-8')
				self.__hpipm.d_ocp_qp_set(c_char_p(field_name_b), i, tmp, self.qp_struct)
		return


	def print_C_struct(self):
		self.__hpipm.d_ocp_qp_print(self.dim.dim_struct, self.qp_struct)

	def codegen(self, file_name, mode):
		file_name_b = file_name.encode('utf-8')
		mode_b = mode.encode('utf-8')
		self.__hpipm.d_ocp_qp_codegen(c_char_p(file_name_b), c_char_p(mode_b), self.dim.dim_struct, self.qp_struct)
		return 

