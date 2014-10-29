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

Given a dataset of phrases (movies reviews), it is demanded to predict the label for the sentiment with 5 different possible values:

- 0 - negative
- 1 - somewhat negative
- 2 - neutral
- 3 - somewhat positive
- 4 - positive

The given dataset is in the TSV format but the toolkit of Stanford uses a PTB format as input and output. The major part of the code
was written to only handle the transformation between these two file types. The main difference between them is that the PTB format
compiles the whole sentence in only one line while the TSV format uses a "Sentence's Identification Code" system.

During the training phase we tried different setups (using tensor, not using it, more phrases for each batch, less phrases, different
sizes of word vector)  once it was the our first time working with this toolkit.

We decided for it because it was written regarding the Socher's paper, a implementation of RNTNs, and during the first trainings it
showed good numbers. Beside the fact it was a good reason to study and understand better the use of neural networks.

After some tries, we realize:

- the result with the entire dataset and the default implementation is better when we don't use the tensor;
- to achieve better results it will be necessary tune the default implementation and not only the training parameter setup.

The best score achieved is 0.62863 (the 124th position in the Kaggle's Leaderboard in Oct, 21st 2014)


The Initial Setup
-------------

After download the code you have to:

- download the [`Stanford NLP - Version 3.4.1`](http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip);
- unzip it;
- copy the jar files (ejml-0.23, javax.json, joda-time, jollyday, stanford-corenlp-3.4.1-models, stanford-corenlp-3.4.1, xom) to
a project folder named "stanford_classpath3_4".
- compile the java code in a project folder named "java_bin"


How to use it
-------------

In the folder script/round04 there is a script named step.sh that describe the sequence of steps to train the model and test 
the dataset. You can use it or run the commands on your own.


Credits
---------

This project was developed by Renato Brandão, you can contact me at
<renatojdk@gmail.com>.

