# -*- coding: utf-8 -*-
"""ML Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jVlOdcKDN42K_R5CTr6qJr0PVC8aOzZE
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras.optimizers import SGD, Adam
from keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import BinaryCrossentropy, SparseCategoricalCrossentropy
from tensorflow.keras.activations import linear, relu, sigmoid
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import log_loss
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.inspection import DecisionBoundaryDisplay
import matplotlib.pyplot as plt

"""Wrote the attributes name manually and read the file"""

attributes = ['parents','has_nurs', 'form', 'children', 'housing', 'finance', 'social','health', 'class']
data = pd.read_csv('http://archive.ics.uci.edu/ml/machine-learning-databases/nursery/nursery.data', names = attributes)

"""A dataset that shows **attributes** such as 

   -parents    :    usual, pretentious, great_pret

   -has_nurs   :    proper, less_proper, improper, critical, very_crit

   -form      :     complete, completed, incomplete, foster

   -children   :    1, 2, 3, more
   
   -housing    :    convenient, less_conv, critical
   
   -finance     :   convenient, inconv
   
   -social     :    non-prob, slightly_prob, problematic
   
   -health      :   recommended, priority, not_recom

**Class Values**

not_recom, recommend, very_recom, priority, spec_prior

Dropping rows with class values recommend since there are only 2 records and might have an effect on the model
"""

data.drop(data[data['class']=='recommend'].index,inplace=True)
print(data)

x = data.drop('class', axis=1)  # Features (input variables)
y = data['class']  # Target variable

encoder=LabelEncoder()
encoder.fit(y)
Y=encoder.transform(y)
Y=pd.Series(Y)
for i in x.keys():
  encoder.fit(x[i])
  x[i]=encoder.transform(x[i])
print(x)

# Split data into training and test sets
x_train, x_test, y_train, y_test = train_test_split(x, Y, test_size=0.2, random_state=42)

# Further split the training set into training and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

mlp_model = Sequential ([
    Dense (25, activation='relu'),
    Dense (15, activation='relu'),
    Dense (5, activation='softmax')
])

mlp_model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
              optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              metrics=['accuracy'])

print(x_train.dtypes)
print(x_val.dtypes)
print(x_test.dtypes)

batch_size = [80,120,160,180,200]
epochs = 29

model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
    filepath='model.hdf5',
    monitor='val_accuracy',
    mode='max',
    save_best_only=True)
models={}
for i in range(len(batch_size)):
  model='run '+str(i+1)
  models[model]=mlp_model.fit(x_train, y_train, 
            batch_size = batch_size[i],
            epochs = epochs,
            callbacks=[model_checkpoint_callback],
            validation_data=(x_val,y_val))

scores={}
for modelN,model in models.items():
  scores[modelN]=max(model.history['val_accuracy'])
print(scores)

y_pred =mlp_model.predict(x_test)
print(y_pred.shape)

y_pred_classes = np.argmax(y_pred, axis=1)
print('Testing Accuracy and Loss: ', mlp_model.evaluate(x_test,y_test))
print('Testing Precision', precision_score(y_test, y_pred_classes,average='macro'))
print('Testing Recall', recall_score(y_test,y_pred_classes,average='macro'))
print('Testing f1 Score: ', f1_score(y_test,y_pred_classes,average='macro'))

"""**Support Vector Machine (SVM) Classification**"""

# Split data into training and test sets
x_train, x_test, y_train, y_test = train_test_split(x, Y, test_size=0.2, random_state=42,shuffle=True)

# Further split the training set into training and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

"""Training the model on the training data set with different parameters to identify the best parameter to be used. Evaluation is done on the validation data set."""

c=[100,200,300,400,500]
deg=[2,3,4]
run=1
for d in deg:
  for c in c:
    svm_model=SVC(kernel='poly', degree=d , C=c,probability=True)
    svm_model.fit(x_train, y_train)
    print("***************")
    print("Run "+str(run)+":")
    print("C= ",c," Degree= ",d)
    print("Loss: ", log_loss(y_val,svm_model.predict_proba(x_val)))
    print("Accuracy: ",accuracy_score(y_val, svm_model.predict(x_val)))
    run+=1

"""Based on the validation set testing we choose the best parameters for the model based on loss and accuracy"""

svm_model = SVC(kernel='poly', degree= 4, C= 400,probability=True)
svm_model.fit(x_train,y_train)
predictions=svm_model.predict(x_test)

encoder.fit(y)
predictionsView=pd.DataFrame(encoder.inverse_transform(predictions))
print(predictionsView)

"""Model Performance on Testing Data"""

print('Testing Accuracy: ',accuracy_score(y_test, predictions))
print('Testing Loss: ', log_loss(y_test,svm_model.predict_proba(x_test)))
print('Testing Precision', precision_score(y_test, predictions,average='macro'))
print('Testing Recall', recall_score(y_test,predictions,average='macro'))
print('Testing f1 Score: ', f1_score(y_test,predictions,average='macro'))

