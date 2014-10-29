Sentiment Analysis - Kaggle Competition
===================================

This is an entry to [Kaggle](http://www.kaggle.com/)'s
[Sentiment Analysis on Movie Reviews](http://www.kaggle.com/c/sentiment-analysis-on-movie-reviews)
competition.

It's written for Python 3.3 and Java 1.7 and works with the [`Stanford CoreNLP`](http://nlp.stanford.edu/software/corenlp.shtml),
a NLP Toolkit released by Stanford that have sentiment tools to train models and annotate corpus using Recursive Neural Networks
and Recursive Neural Tensor Network.


General Description
-----------------

Given a dataset of phrases (movie reviews), it is demanded to predict the label for the sentiment with 5 different possible values:

0 - negative
1 - somewhat negative
2 - neutral
3 - somewhat positive
4 - positive

The given dataset has the TSV format and the toolkit uses a PTB format as input and output.

The major part of the code written is to manipulate the transformation between these two file types. The main difference between them
is that the PTB format compiles the whole sentence in only one line while the CSV format uses a "Sentence Id Code" system.

The Initial Setup
-------------

After download the code you have to:

- download the [`Stanford NLP - Version 3.4.1`](http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip);
- unzip it;
- copy the jar files (ejml-0.23, javax.json, joda-time, jollyday, stanford-corenlp-3.4.1-models, stanford-corenlp-3.4.1, xom) to
the project folder named "stanford_classpath3_4".
- compile the java code in the project folder named "java_bin"


How to use it
-------------

In the folder script/round04 there is a script named step.sh that describe the sequence of steps to train the model and test 
the dataset. You can use it or run the commands on your own.


Credits
---------

This project was developed by Renato Brandão, you can contact me at
<renatojdk@gmail.com>.

