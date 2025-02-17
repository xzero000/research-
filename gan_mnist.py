import tensorflow as tf
#import tensorflow.compat.v1 as tf
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
##import torchvision.datasets.mnist as mnist
import numpy
import time
import datetime

##path = '/home/xzero000/dataset/MNIST/raw'
###root = "./mnist/raw/"
##train_set = (
##    mnist.read_image_file(os.path.join(path,'train-images-idx3-ubyte')),
##    mnist.read_label_file(os.path.join(path,'train-labels-idx1-ubyte'))
##    )
##
##test_set = (
##    mnist.read_image_file(os.path.join(path,'t10k-images-idx3-ubyte')),
##    mnist.read_label_file(os.path.join(path,'t10k-labels-idx1-ubyte'))
##    )
##
## pip --no-cache-dir install tensorflow


from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/")

#generator
def generator(z,reuse = False):
    with tf.variable_scope('generator',reuse = reuse):
        #initializers
        w_init = tf.truncated_normal_initializer(mean = 0, stddev = 0.02)
        b_init = tf.constant_initializer(0.)

        #1st hidden layer
        G_w0 = tf.get_variable('G_w0',[100,256],initializer = w_init)
        G_b0 = tf.get_variable('G_b0',[256],initializer = b_init)
        G_fc0 = tf.nn.relu(tf.matmul(z,G_w0)+G_b0)

        #2nd hidden layer
        G_w1 = tf.get_variable('G_w1',[256,512],initializer = w_init)
        G_b1 = tf.get_variable('G_b1',[512],initializer = b_init)
        G_fc1 = tf.nn.relu(tf.matmul(G_fc0,G_w1)+G_b1)

        #3rd hidden layer
        G_w2 = tf.get_variable('G_w2',[512,1024],initializer = w_init)
        G_b2 = tf.get_variable('G_b2',[1024],initializer = b_init)
        G_fc2 = tf.nn.relu(tf.matmul(G_fc1,G_w2) + G_b2)

        #output hidden layer
        G_w3 = tf.get_variable('G_w3',[1024,784],initializer = w_init)
        G_b3 = tf.get_variable('G_b3',[784],initializer = b_init)
        f_image = tf.nn.tanh(tf.matmul(G_fc2,G_w3) + G_b3)
        
    return f_image

# discriminator
def discriminator(image,drop_out,reuse = False):
    with tf.variable_scope('discriminator',reuse = reuse):
        #initializers
        w_init = tf.truncated_normal_initializer(mean = 0, stddev = 0.02)
        b_init = tf.constant_initializer(0.)

        #1st hidden layer
        D_w0 = tf.get_variable('D_w0',[784,1024],initializer = w_init)
        D_b0 = tf.get_variable('D_b0',[1024],initializer = b_init)
        D_fc0 = tf.nn.relu(tf.matmul(image,D_w0)+D_b0)
        D_fc0 = tf.nn.dropout(D_fc0,drop_out)
        
        #2nd hidden layer
        D_w1 = tf.get_variable('D_w1',[1024,512],initializer = w_init)
        D_b1 = tf.get_variable('D_b1',[512],initializer = b_init)
        D_fc1 = tf.nn.relu(tf.matmul(D_fc0,D_w1) + D_b1)
        D_fc1 = tf.nn.dropout(D_fc1,drop_out)

        #3rd hidden layer
        D_w2 = tf.get_variable('D_w2',[512,256],initializer = w_init)
        D_b2 = tf.get_variable('D_b2',[256],initializer = b_init)
        D_fc2 = tf.nn.relu(tf.matmul(D_fc1,D_w2)+D_b2)
        D_fc2 = tf.nn.dropout(D_fc2,drop_out)
             
        #output layer
        D_w3 = tf.get_variable('D_w3',[256,1],initializer = w_init)
        D_b3 = tf.get_variable('D_b3',[1],initializer = b_init)
        output = tf.sigmoid(tf.matmul(D_fc2,D_w3) + D_b3)
        
        return output

#save image
def save_f_image(index,z_sample):
    fig = plt.figure(figsize = (4,4))
    gs = gridspec.GridSpec(4,4)
    gs.update(wspace = .005, hspace = 0.05)

    for i,sample in enumerate(z_sample):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28,28),cmap = 'gray')
    plt.savefig('gan_fig_1e-8/{}.png'.format(str(index).zfill(3)),bbox_inches = 'tight')
    plt.close(fig)    

#input placeholder
x = tf.placeholder(tf.float32, shape = (None,784))
z = tf.placeholder(tf.float32, shape = (None,100))
drop_out = tf.placeholder(tf.float32)

#Generate fake image and discriminate real and fake
f_sample = generator(z)
D_real = discriminator(x,drop_out)
D_fake = discriminator(f_sample,drop_out,reuse = True)

# loss for generator and discriminator
D_loss = -tf.reduce_mean(tf.log(tf.clip_by_value(D_real,1e-8,1.0))+ tf.log(tf.clip_by_value(1-D_fake,1e-8,1.0)))
G_loss = -tf.reduce_mean(tf.log(tf.clip_by_value(D_fake,1e-8,1.0)))
'tf.log(tf.clip_by_value(tf.sigmoid(self.scores),1e-8,1.0)'
"""
eps = 1e-2
D_loss = tf.reduce_mean(-tf.log(D_real + eps) - tf.log(1 - D_fake + eps))
G_loss = tf.reduce_mean(-tf.log(D_fake + eps))
"""

#set hyper paramatrics
batch_size = 100
l_rate = 0.01
train_epoch = 5000
epoch = 0
index = 0

#trainable variables for each network
t_vars = tf.trainable_variables()
D_vars = [var for var in t_vars if 'D_' in var.name]
G_vars = [var for var in t_vars if 'G_' in var.name]

#optimizer for generator and dirvriminator
learning_rate = tf.placeholder(tf.float32,shape = [])
D_train = tf.train.AdamOptimizer(l_rate).minimize(D_loss,var_list = D_vars)
G_train = tf.train.AdamOptimizer(l_rate).minimize(G_loss,var_list = G_vars)

#setup tf session
gpu_options = tf.GPUOptions(allow_growth = True)
sess = tf.Session(config = tf.ConfigProto(gpu_options = gpu_options))

init = tf.global_variables_initializer()
sess.run(init)
saver = tf.train.Saver()

#normalize
train_set = (mnist.train.images -0.5)/0.5

#default_noise
test_z = np.random.normal(0,2,(16,100))

t1 = time.time()
print('start train')

while epoch <= train_epoch:
    #G_losses = []
    #D_losses = []
    #sess.graph.finalize(), for prevent memory explode

    #Save all fake image
    if epoch %50 ==0:
        fake_image = sess.run(f_sample,{z:test_z,drop_out:0.0})
        save_f_image(index,fake_image)
        index += 1

    #start training
    for i in range(0,train_set.shape[0],batch_size):
        sess.graph.finalize()
        input_x = train_set[i:i+batch_size]
        input_z = np.random.normal(0,1,(batch_size,100))

        sess.run(D_train,{x:input_x,z:input_z,drop_out:0.1})
        loss_d = sess.run(D_loss,{x:input_x,z:input_z,drop_out:0.1})
        #D_losses.append(loss_d)

        input_z = np.random.normal(0,1,(batch_size,100))

        sess.run(G_train,{z:input_z,drop_out:0.3})
        loss_g = sess.run(G_loss,{z:input_z,drop_out:0.1})
        #G_losses.append(loss_g)
        #if (i/batch_size)%500 == 0:
         #   print('%d,'%(i/batch_size),end = '')

    epoch += 1
    if epoch == 50:
        l_rate = 0.01
    if epoch == 200:
        l_rate = 0.001
    if epoch == 500:
        l_rate = 0.0002
    
    print("\n@epoch of {}, D_loss:{}, G_loss:{}, time: {}".format(epoch,loss_d,loss_g,datetime.datetime.now()))
    

save_path = saver.save(sess,'/home/r05942072/git/research/model/gan_mnist_test_1e-8.ckpt')
print('Model saved in path:%s'%save_path)
        
        






    
    
