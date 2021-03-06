import re
from math import sqrt
import nltk
import csv
import argparse
import time
from collections import OrderedDict
from sklearn.feature_extraction.text import CountVectorizer
import numpy
import threading
import os

class KNN:

    def __init__(self):
        self.train_vectors = OrderedDict({})
        self.y = []
        self.id = []
        self.knn_results = {}
        self.categories = {}
        self.test_vectors = OrderedDict({})
        self.log_file = None

    def write_to_log(self,text):
        with open(self.log_file,'a') as logger:
            logger.write(text+'\n')

    def vectorize_training_and_test_data(self, trainfile,testfile):
        self.write_to_log("-------------Vectorizing training and test data--------------")
        X = []
        X_test = []
        with open(trainfile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                X.append(row['Text'])
                self.y.append(row['Category'])

        with open(testfile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                X_test.append(row['Text'])
                self.id.append(row['Id'])
        vec = CountVectorizer(input='content',analyzer='char',decode_error='ignore',stop_words=None,ngram_range=(1,1))
        self.train_vectors = vec.fit_transform(X,self.y).toarray()
        self.test_vectors = vec.transform(X_test).toarray()

    def predict_knn(self,k,outfile,start,end):
        self.write_to_log("-------------Calculating nearest neighbours from row_id: "+str(start)+" to row_id: "+str(end)+"--------------")
        f = open(outfile, 'a')
        # f.write('Id,Category\n')
        predictions = {}
        neighbours = {}
        for test_row in range(start,end):
            # if int(test_row)%1000 == 0: self.write_to_log("Calculating distances and prediction for row_id: "+str(test_row))
            neighbours[test_row] = zip(range(len(self.train_vectors)),numpy.sqrt(numpy.sum((self.train_vectors - self.test_vectors[test_row])**2,axis=1)))
            neighbours[test_row] = sorted(neighbours[test_row], key=lambda tup: tup[1])[0:k]
            predictions[test_row] = {}
            for i in range(k):
                row_id = neighbours[test_row][i][0]
                lang = self.y[row_id]
                try:
                    predictions[test_row][lang] += 1
                except KeyError:
                    predictions[test_row][lang] = 1
            language_predicted = sorted(predictions[test_row].iteritems(), key=lambda (ke,v): (v,ke), reverse=True)[0][0]
            f.write(str(self.id[test_row])+','+str(language_predicted)+'\n')
        self.write_to_log("-------------Completed calculating nearest neighbours from row_id: "+str(start)+" to row_id: "+str(end)+"--------------")
        f.close()

    def vectorize_training_data(self, textfile):
        self.write_to_log("-------------Vectorizing training data--------------")
        word_count_in_languages = {}
        with open(textfile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_id = row['Id']
                if int(row_id)%10000 == 0: self.write_to_log("Vectorizing training row: "+row_id)
                self.categories[row_id] = row['Category']
                if self.train_vectors.get(row_id) is None: self.train_vectors[row_id] = {}
                for word in nltk.word_tokenize(row['Text']):
                    try:
                        self.train_vectors[row_id][word] += 1
                    except KeyError:
                        self.train_vectors[row_id][word] = 1
                for word, freq in self.train_vectors[row_id].iteritems():
                    self.train_vectors[row_id][word] = float(self.train_vectors[row_id][word]) / float(sum(self.train_vectors[row_id].values()))
        self.write_to_log("-------------Completed vectorizing training data--------------")

    def vectorize_test(self, testfile):
        self.write_to_log("-------------Vectorizing test data--------------")
        with open(testfile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_id = row['Id']
                if int(row_id)%1000 == 0: self.write_to_log("Vectorizing test row: "+row_id)
                self.test_vectors[row_id] = {}
                for word in nltk.word_tokenize(row['Text']):
                    try:
                        self.test_vectors[row_id][word] += 1
                    except KeyError:
                        self.test_vectors[row_id][word] = 1
                for word in nltk.word_tokenize(row['Text']):
                    self.test_vectors[row_id][word] = float(self.test_vectors[row_id][word]) / float(sum(self.test_vectors[row_id].values()))
        self.write_to_log("-------------Completed vectorizing test data--------------")

    def knn_calc(self, k, outfile):
        self.write_to_log("-------------Calculating nearest neighbours--------------")
        f = open(outfile, 'w')
        f.write('Id,Category\n')
        predictions = {}
        for test_row in self.test_vectors.keys():
            self.knn_results[test_row] = {}
            neighbours = {}
            if int(test_row)%10000 == 0: self.write_to_log("Calculating distances for row_id: "+test_row)
            for row_id in self.train_vectors.keys():
                neighbours[row_id] = sqrt(sum({word: (self.test_vectors[test_row][word] - self.train_vectors[row_id].get(word,0))**2 for word in self.test_vectors[test_row].keys()}.values()))
            neighbours = sorted(neighbours.iteritems(), key=lambda (ke,v): (v,ke))[0:k]
            if int(test_row)%10000 == 0: self.write_to_log("Predicting language for test row_id: "+test_row)
            predictions[test_row] = {}
            for i in range(k):
                row_id = neighbours[i][0]
                lang = self.categories[row_id]
                try:
                    predictions[test_row][lang] += 1
                except KeyError:
                    predictions[test_row][lang] = 1
            language_predicted = sorted(predictions[test_row].iteritems(), key=lambda (k,v): (v,k), reverse=True)[0][0]
            f.write(str(test_row)+','+str(language_predicted)+'\n')
        f.close()

    def run_knn(self):
        parser = argparse.ArgumentParser(description='KNN algorithm')
        parser.add_argument('-f','--text', nargs=1, help='CSV text and language file',required=True)
        parser.add_argument('-k','--knn', nargs=1, help='Number of nearest neighbours',required=True)
        parser.add_argument('-t','--test', nargs=1, help='CSV test file',required=True)
        parser.add_argument('-o','--out', nargs=1, help='output CSV file',required=True)
        parser.add_argument('-l','--logfile', nargs=1, help='log file',required=True)
        parser.add_argument('-optimize', action='store_true', help='Perform threading for knn and use CountVectorizer to vectorize data')
        args = parser.parse_args()
        self.log_file = args.logfile[0]
        if args.optimize:
            # Running 8 threads to each compute 1000 test rows at a time
            self.vectorize_training_and_test_data(args.text[0], args.test[0])
            threads = []
            i=0
            outfile = args.out[0]
            outfiles = [None] * 8
            while i < len(self.test_vectors):
                self.write_to_log("-------------Starting 8 new threads--------------")
                self.write_to_log("-------------Predictions so far: "+str(i)+"--------------")
                t_id=0
                en = 0
                for j in range(8):
                    t_id+=1
                    st = i
                    en = i+1000
                    if outfiles[j] is None:
                        dir_name = os.path.dirname(outfile)
                        base = os.path.basename(outfile)
                        f = os.path.splitext(base)
                        outfiles[j] = os.path.join(dir_name,f[0]+str(t_id)+f[1])
                        if os.path.isfile(outfiles[j]): os.remove(outfiles[j])
                    if en > len(self.test_vectors):
                        en = len(self.test_vectors)
                    t = threading.Thread(target=self.predict_knn, args = (int(args.knn[0]),outfiles[j],st,en))
                    threads.append(t)
                    t.start()
                    i = en
                    if en >= len(self.test_vectors):
                        break
                for x in threads:
                    x.join()
                if i >= len(self.test_vectors):
                    break
        else:
            self.vectorize_training_data(args.text[0])
            self.vectorize_test(args.test[0])
            self.knn_calc(int(args.knn[0]), args.out[0])


knn = KNN()
knn.run_knn()
