#!/bin/bash

CSV_PATH="/tmp/csv"
TOOLS_DIR="/tmp/tools"
KFOLD_DIR="$CSV_PATH/kfold"

# Compare generated csv with the actual answer
function comparecsv() {
    k="$1"
    path="$2"
    python "$TOOLS_DIR/comparecsv.py" \
        -s "$KFOLD_DIR/results/$path/out$k" \
        -a "$KFOLD_DIR/valid/test$k" \
        | command grep -i "total"
}

# Vanilla Naive-bayes
function naivebayes() {
    k=$1
    outdir="NB"
    echo "Executing Naive-Bayes for k=$k"
    mkdir -p "$KFOLD_DIR/results/$outdir/"
    python "$TOOLS_DIR/naivebayes.py" \
        -i "$KFOLD_DIR/train/train$k" \
        -t "$KFOLD_DIR/test/test$k" \
        -o "$KFOLD_DIR/results/$outdir/out$k" > /dev/null

    comparecsv "$k" "$outdir"
}

# Naive-bayes with filter 1
function naivebayes_f1() {
    k=$1
    outdir="NB+F1"
    rval="0.004"
    echo "Executing Naive-Bayes for k=$k and r=$rval"
    mkdir -p "$KFOLD_DIR/results/$outdir/"
    python "$TOOLS_DIR/naivebayes.py" \
        -i "$KFOLD_DIR/train/train$k" \
        -t "$KFOLD_DIR/test/test$k" \
        -o "$KFOLD_DIR/results/$outdir/out$k" \
        -r "$rval" > /dev/null

    comparecsv "$k" "$outdir"
}

# Naive-bayes with filter 1 and filter 2
function naivebayes_f1_f2() {
    k=$1
    outdir="NB+F1+F2"
    rval="0.004"
    echo "Executing Naive-Bayes for k=$k, r=$rval and strict mode enabled"
    mkdir -p "$KFOLD_DIR/results/$outdir/"
    python "$TOOLS_DIR/naivebayes.py" \
        -i "$KFOLD_DIR/train/train$k" \
        -t "$KFOLD_DIR/test/test$k" \
        -o "$KFOLD_DIR/results/$outdir/out$k" \
        -r "$rval" \
        -s > /dev/null

    comparecsv "$k" "$outdir"
}

# Naive-bayes with filter 1, filter 2, Recover Data
function naivebayes_f1_f2_rd() {
    k=$1
    outdir="NB+F1+F2+RD"
    echo "Executing Recover data for k=$k"
    mkdir -p "$KFOLD_DIR/results/$outdir"
    python "$TOOLS_DIR/recover-data.py" \
        -d "$KFOLD_DIR/train-em/train$k" \
        -t "$KFOLD_DIR/test-em/test$k" \
        -o "$KFOLD_DIR/results/$outdir/merge$k" > /dev/null

    python "$TOOLS_DIR/manipsubmit.py" \
        -i "$KFOLD_DIR/results/NB+F1+F2/out$k" \
        -m "$KFOLD_DIR/results/$outdir/merge$k-0" \
        -o "$KFOLD_DIR/results/$outdir/out$k" > /dev/null
    
    comparecsv "$k" "$outdir"
}

# Naive-bayes with filter 1, filter 2, Recover Data and Exact Match
function naivebayes_f1_f2_rd_em() {
    k=$1
    outdir="NB+F1+F2+RD+EM"
    echo "Executing Exact Match for k=$k"
    mkdir -p "$KFOLD_DIR/results/$outdir"
    python "$TOOLS_DIR/exact-match.py" \
        -d "$KFOLD_DIR/train-em/train$k" \
        -t "$KFOLD_DIR/test-em/test$k" \
        -o "$KFOLD_DIR/results/$outdir/merge$k" > /dev/null

    python "$TOOLS_DIR/manipsubmit.py" \
        -i "$KFOLD_DIR/results/NB+F1+F2+RD/out$k" \
        -m "$KFOLD_DIR/results/$outdir/merge$k" \
        -o "$KFOLD_DIR/results/$outdir/out$k" > /dev/null

    comparecsv "$k" "$outdir"
}

for k in {1..10}
do
    naivebayes $k
    naivebayes_f1 $k
    naivebayes_f1_f2 $k
    naivebayes_f1_f2_rd $k
    naivebayes_f1_f2_rd_em $k
    echo "----------------------"
done
