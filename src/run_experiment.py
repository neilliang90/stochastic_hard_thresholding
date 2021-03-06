# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 21:14:55 2019

@author: gul15103
"""

import svrg_ht
import sgd_ht
import hsgd_ht
import gd_ht
import scsg_ht

import argparse

parser = argparse.ArgumentParser(description='hardthresholding methods')
parser.add_argument('--epoch', default=50, type=int, metavar='N', help='number of total epochs to run')
parser.add_argument('--file_path',default='F:/Users/gul15103/Desktop/E2006.test',  type=str)
parser.add_argument('--output_folder', default='../logs/mnist', type=str)
parser.add_argument('--batchsize', default=1, type=int, metavar='N', help='mini-batch size (default: 128),only used for train')
parser.add_argument('--htk', default=200, type=int)
parser.add_argument('--B_type', default=1, type=int)
parser.add_argument('--opt', default='sgd', type=str)
parser.add_argument('--data_type', default='ridge', type=str)
parser.add_argument('--regularizer', default=1e-5, type=float)
parser.add_argument('--etas', nargs='+', type=float)
parser.add_argument('--B_types', nargs='+', type=int)

args = parser.parse_args()

#f= 'F:/Users/gul15103/Desktop/simulate_data1.npz' #1000_2500_0.5
f= args.file_path#'F:/Users/gul15103/Desktop/mnist.scale'
epoch =args.epoch
batch_size = args.batchsize
if args.data_type =='multi':
    loss = 'multi_class_softmax_regression'
    multi_class = True
elif  args.data_type =='binary':
    loss = 'logistic'
    multi_class = False
elif  args.data_type =='ridge':
    loss = 'ridge'
    multi_class = False
    
batch_size_B_type='fixed'
ht_k=args.htk
log_interval=1
regularizer = args.regularizer
output_folder = args.output_folder


etas = args.etas

for eta  in etas:
  if args.opt == 'svrg':
      svrg_ht.svrg_ht( f,regularizer,  epoch, batch_size,  stepsize = eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss ,ht_k=ht_k, log_interval=log_interval,output_folder=output_folder, multi_class= multi_class)
  elif args.opt == 'gd':
    hsgd_ht.sgd_ht( f,regularizer,  epoch, batch_size,  stepsize = eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss , ht_k=ht_k,log_interval=log_interval, output_folder=output_folder , multi_class= multi_class)
    #gd_ht.gd_ht( f,regularizer,  epoch, batch_size,  eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss , ht_k=ht_k ,log_interval=log_interval, output_folder=output_folder)
  elif args.opt == 'sgd':
    sgd_ht.sgd_ht( f,regularizer,  epoch, batch_size,  stepsize = eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss , ht_k=ht_k ,log_interval=log_interval, output_folder=output_folder, multi_class= multi_class)
  elif args.opt == 'scsg':
     for batch_size_B in args.B_types:
             scsg_ht.scsg_ht( f, regularizer, epoch, batch_size_B,batch_size_B_type,batch_size,  stepsize = eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss , ht_k=ht_k, log_interval=log_interval, output_folder=output_folder , multi_class= multi_class)
