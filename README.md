# Language classification
### by team 2045

Our problem is a Dialog Language Classification task. The goal is to devise a machine learning algorithm to analyze short conversations, and automatically classify them according to the language of the conversation. There are five languages in the corpus: {0: Slovak, 1: French, 2: Spanish, 3: German, 4: Polish}

This is a project for COMP-551 Applied Machine Learning. For this task, we would be implementing Naive Bayes and kNN from scratch, and trying other ML algorithms using scikit-learn.

## Commands
*All scripts used in this section are available under `tools/python/` directory*

**All scripts has been tested on &ast;nix machines only, and there is no guarantee to work on other platforms**

### Generate csv files

#### Generate an enhanced training set csv
*Merge `train_set_x.csv` and `train_set_y.csv` into a single file. Furthermore, convert all characters to lower case and place a single whitespace between each two consecutive characters*
```
python3 csv2csv.py \
    -t train_set_x.csv \
    -l train_set_y.csv \
    -o train_set_xy_1.csv \
    -a no_space lower space
```

*Merge `train_set_x.csv` and `train_set_y.csv` into a single file. Furthermore, convert all characters to lower case, remove all whitespaces and sort each sentence lexically*
```
python3 csv2csv.py \
    -t train_set_x.csv \
    -l train_set_y.csv \
    -o train_set_xy_2.csv \
    -a no_space lower sort_lex
```

*Create an enhanced `test_set_x.csv` file. In the new file, remove all whitespaces and sort each sentence lexically*
```
python3 maniptest.py \
    -i test_set_x.csv \
    -o test_set_x_1.csv \
    -a no_space sort_lex
```

### kNN
##### To run kNN from scratch:
*To run non-optimized knn (vectorization term frequency ratio and distance computation is row-wise)*
```
python2 knn.py \
    -f train_set_xy_1.csv \
    -t test_set_x.csv \
    -k <k_value> \
    -o <file_to_output_predictions> \
    -l <file_to_log_to>
```
*To run optimized knn (threaded, CountVectorizer for vectorization, distance computation is matrix level)*
```
python2 knn.py \
    -optimize \
    -f train_set_xy_1.csv \
    -t test_set_x.csv \
    -k <k_value> \
    -o <file_to_output_predictions> \
    -l <file_to_log_to>
```
##### To run kNN using scikit:
```
python2 knn-library.py \
    -f train_set_xy_1.csv \
    -t test_set_x.csv \
    -k <k_value> \
    -o <file_to_output_predictions>
```

### Naive-Bayes
#### To run Naive-Bayes
*Wihtout filters*
```
python3 naivebayes.py \
    -i train_set_xy_1.csv \
    -t test_set_x.csv \
    -o NB.csv
```

*With first filter*
```
python3 naivebayes.py \
    -i train_set_xy_1.csv \
    -t test_set_x.csv \
    -r 0.004 \
    -o NB*.csv
```

*With first and second filters*
```
python3 naivebayes.py \
    -i train_set_xy_1.csv \
    -t test_set_x.csv \
    -r 0.004 \
    -s \
    -o NB**.csv
```

### Anagram Detection
#### To run Anagram Detection
*Without extension*
```
python3 anagrams.py \
    -d train_set_xy_2.csv \
    -t test_set_x_1.csv \
    -p 2 \
    -o AD.csv
```

*With extension*
```
python3 anagrams.py \
    -d train_set_xy_2.csv \
    -t test_set_x_1.csv \
    -p 1 2 \
    -o AD*.csv
```
#### To merge Anagram Detection into Naive-Bayes
```
python3 manipsubmit.py \
    -i NB**.csv \
    -m AD*.csv \
    -o NB**+AD*.csv
```
### Random Forests, Multilayer Perceptron, Logistic Regression, Decision Trees, and Multinomial Naive Bayes (sklearn)
#####

*Make sure to download the <a href="https://goo.gl/Bvm8t7">csv.tar.gz</a> for the required train and test files*  
*To run these algorithms with enhanced k-folds:
```
python2 properKFold_scikit.py /path-to-csv-kfolds-folder-that-you-downloaded/
```
*To run these algorithms:
```
python2 rf_lr_mlp_dt.py train_set_xy_1.csv
```
*To run these algorithms AND plot the graph:
```
python2 rf_lr_mlp_dt.py train_set_xy_1.csv -plot
```
### Compare 2 CSV files (Header: Id,Category)
```
python3 comparecsv.py \
    -s new-submit.csv \
    -a old-submit.csv
```
*Note: This script is useful to compare locally the output difference between a previously submitted csv file and a new generated one.*

### Run Cross-Validation
*Make sure to download the <a href="https://goo.gl/Bvm8t7">csv.tar.gz</a> for the required train and test files*  
*Edit file `kfold.sh` and set the path to downloaded/extracted csv directory*
```
bash kfold.sh
```
