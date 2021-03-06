#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 13:24:52 2018

@author: Neil
"""

#import sklearn
import numpy as np

import os
#import copy
#import time
#from operator import add
import time
import Loss
import Util
#import argparse
from tensorboardX import SummaryWriter

def scsg_ht( f,regularizer , epoch,batch_size_B,batch_size_B_type,  batch_size , stepsize= 10**-5,  stepsize_type = "fixed", verbose = False, optgap = 10**(-3 ), loss = 'logistic', ht_k=300,log_interval=1,output_folder='../logs/', multi_class= False):
  '''
  INPUT:
  x : data
  y : vector for label 1 or 0
  K : number of outest iterations
  P : number of parallel precossors
  batch_size4SVRG :
  batch_size4H
  stepsize  : default 10**-5
  stepsize_type : fixed, decay 1/t, sqrt decay 1/sqrt( t )
  OUTPUT:
  '''
  # global FILENAME
  # FILENAME = outfile

  # print FILENAME
  # logging.basicConfig(level=logging.DEBUG, filename=FILENAME, filemode='w')

  if 'simulate' in f:
      data = np.load( f )
      x= data['x']
      y= data['y']
  else:
      x, y = Util.readlibsvm(f)
  if 'news20' in f:
      y = y -1
      #x = sklearn.preprocessing.normalize( x )
      
  index = np.arange(np.shape(x)[0])
  np.random.shuffle(index)
  x= x[index, :]
  y = y[index ]
  #label = (label == 1 )* 1
  folder_name = os.path.basename(f) + '_loss_' + str(loss)  +'_opt_scsg_'+ 'stepsize_'+str( stepsize)+'batchsizeB_'+ str( batch_size_B)+'_'+str( batch_size_B_type)+'_ht_k_'+ str(ht_k)+'_log_interval_'+ str(log_interval)+'_epoch_'+ str(epoch)
  logger = SummaryWriter(output_folder+folder_name)
  file = open(output_folder+folder_name+str(".txt"),"w")
  
  file.write( "The dataset : " + str( f) + '\n' )
  file.write( "The number of instances N : " + str( x.shape[0])  + '\n')
  file.write( "The number of features p : " + str( x.shape[1])  + '\n')
  file.write( "The step size : " + str(  stepsize ) + '\n' )
  file.write( "The epoch : " + str(  epoch )  + '\n')
  file.write( "The loss type: " + str(loss)  + '\n')
  file.write( "The regularizer : " + str(  regularizer ) + '\n' )
  file.write( "The ht_k : " + str(  ht_k ) )
  file.write( "The batch_size : " + str(  batch_size )  + '\n')

  file.write('num_epoch,num_IFO,num_HT,loss\n') 
  
  if loss=='logistic':
    loss = Loss.LogisticLoss_version2()
  elif loss == 'svm' :
    loss = Loss.svm_quadratic()
  elif loss == 'ridge' :
    loss = Loss.ridge_regression()
  elif loss == 'multi_class_softmax_regression':
    loss = Loss.multi_class_softmax_regression()
   #regularizer = 1/x.shape[0]
  
  #loss = Loss.ridge_regression()
  print( "The dataset : " + str( f) )
  print( "The number of instances N : " + str( x.shape[0]) )
  print( "The number of features p : " + str( x.shape[1]) )
  print( "The batch size for SGD : " + str( batch_size ) )
  print( "The step size : " + str(  stepsize ) )
  print( "The epoch : " + str(  epoch ) )
  print( "The loss type: " + str(loss) )
  print( "The regularizer : " + str(  regularizer ) )
  
  
  if multi_class:
      w  = np.zeros((x.shape[1],len( np.unique( y ))))
  else: 
      w = np.zeros(x.shape[1],)
   
  # ---------------------------------------------
 
  #store information
  obj_list  = list();
  t0 = time.time()
  iteration=0
  N_total = 0
  number_IFO=0
  
  for k in range (10**5):
    if not batch_size_B_type == 'fixed':
        batch_size_B = k #int( 1/( 1-1/480)**k)
    #print("master iteration ", k)
      #setup stepsize
    if stepsize_type == "fixed":
      eta = stepsize
    elif stepsize_type == "decay":
      eta = 1./( k+1) 
    elif stepsize_type == "sqrtdecay":
    #eta = 1/np.sqrt(k*L + t +1 )
      eta = stepsize*1./np.sqrt( k +1)
    elif stepsize_type == "squaredecay":
      eta = ( 1/np.square(k + 1 ))
    
    sample_id = np.random.randint(x.shape[0]-batch_size_B, size=1)
    sample_id = sample_id[0]
    w_multi = np.copy(w)
    u = loss.grad(x[sample_id:sample_id+batch_size_B], y[sample_id:sample_id+batch_size_B], w, regularizer)
    
    #N = np.random.geometric( 1/batch_size_B )
    N=int( batch_size_B/batch_size)
    N_total = N_total + N
    #number_IFO+=batch_size_B
    for t in range(N):

      #print("master iteration ", k, t)
      if k <1:
        #lock.acquire()
        sample_id = np.random.randint(x.shape[0]-batch_size, size=1)
        sample_id = sample_id[0]
        g1 = loss.grad(x[sample_id:sample_id+batch_size], y[sample_id:sample_id+batch_size], w, regularizer)
        #print(multiprocessing.current_process(), "Grad w ", w[ 0:3])
        #lock.release()
        v = g1
      else:
        #lock.acquire()
        sample_id = np.random.randint(x.shape[0]-batch_size, size=1)
        sample_id = sample_id[0]
        g1 = loss.grad(x[sample_id:sample_id+batch_size], y[sample_id:sample_id+batch_size], w, regularizer)
        #print(multiprocessing.current_process(), "Grad w ", w[ 0:3])
        #lock.release()
        g2 = loss.grad(x[sample_id:sample_id+batch_size], y[sample_id:sample_id+batch_size], w_multi, regularizer )
        v = g1 - g2 + u
        
        #print( 'w_multi : ', np.square( np.linalg.norm( w_multi )))
      
      Hv= -v
      #print( 'w : ', np.square( np.linalg.norm( w )))
      #print(multiprocessing.current_process(), "Before Update w ", w[0:3], w[ -3:-1])
      w = w + eta*Hv
      #w[ np.absolute(w).argsort()[:-ht_k][::-1]] = 0
      if multi_class:
          for j in range( w.shape[1]):
              w[ np.absolute(w[:,j]).argsort()[:-ht_k][::-1], j ] = 0
      else:
          w[ np.absolute(w).argsort()[:-ht_k][::-1]] = 0
         #print(multiprocessing.current_process(), "After Update w ", w[0:3], w[ -3:-1])
      iteration = iteration + 1
      number_IFO+=2*batch_size
      if number_IFO/x.shape[0] > epoch:
        return
    #--------------------------------------
      if t % log_interval == 0:
        #obj_temp = loss.obj( x, y, w, regularizer )/loss.obj( x, y, np.zeros(x.shape[1],), regularizer )
        obj_temp = loss.obj( x, y, w, regularizer )
        #if k>0:
        time_k = time.time()
        #print( 'Epoch: '+ str(N_total/x.shape[0] + t/x.shape[0]) +', data passes : '+ str((N_total/x.shape[0])*2 + N/x.shape[0]+ t/x.shape[0])+ ', time :' + str(time_k - t0 ))
            #store informations
            #if verbose:
        #print(  "objective value  %.30f" % obj_temp)
        #print( "Norm for w : ", np.square( np.linalg.norm( w )))
        obj_list.append(obj_temp)
        if k>0 and np.abs( obj_list[-1] - obj_list[ -2 ] ) < optgap:
          print( "Optimality gap tolerance reached : optgap " + str( optgap ))
          break
              #return obj_list, datapasses_list, time_list
        #print( 'Loss:{:.4f}, Accuracy: {:.1f}'.format(loss.item(), accuracy))
            
        # ================================================================== #
        #                        Tensorboard Logging                         #
        # ================================================================== #
    
        # 1. Log scalar values (scalar summary)
        print( 'loss ' + str( obj_temp)) 
        logger.add_scalar('loss_number-IFO',obj_temp, number_IFO)
        logger.add_scalar('loss_number-HT', obj_temp, iteration)
        file.write(str( number_IFO/x.shape[0])+','+str( number_IFO)+','+str(iteration)+','+ str(obj_temp)+'\n')  
  file.close()
  
def main(batch_size_B = 5000, batch_size_B_type = 'fixed',batch_size = 1, eta=0.05, epoch = 1, loss = 'logistic'):
  #f = sys.argv[1]
  #dataset = 'real-sim'
  
  #f = '/Users/Neil/Desktop/E2006.train'
  #f = '../data/' + dataset
  #f= '../data/real-sim'
  
  
  
  
  f= 'F:/Users/gul15103/Desktop/news20.scale'
  #eta=0.1
  
  loss = 'multi_class_softmax_regression'
  regularizer=0.001  
  
  #logging.basicConfig( level=logging.DEBUG)
  
  #for eta in [0.5, 0.1, 0.01, 0.05] :
   #   for batch_size_B in [100, 500, 1000, 5000]:
  scsg_ht( f, regularizer, epoch, batch_size_B,batch_size_B_type, batch_size, stepsize= eta, stepsize_type = "fixed", verbose = True, optgap = 10**(-30), loss = loss , ht_k=200, multi_class= True)
  


if __name__== "__main__":
  main()
