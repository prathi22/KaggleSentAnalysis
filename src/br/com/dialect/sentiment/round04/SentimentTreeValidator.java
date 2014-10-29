package br.com.dialect.sentiment.round04;

import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.neural.rnn.RNNCoreAnnotations;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.sentiment.CollapseUnaryTransformer;
import edu.stanford.nlp.sentiment.SentimentCostAndGradient;
import edu.stanford.nlp.sentiment.SentimentModel;
import edu.stanford.nlp.sentiment.SentimentUtils;
import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.Trees;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

/**
 * The main goal of this class is to binarize and validate each phrase to guarantee that they have a valid PTB format.
 *
 * As well, it can attach the sentiment score if a sentiment model and a test file is informed.
 */
public class SentimentTreeValidator {
  public SentimentTreeValidator() {} // static methods only


  private static int setPredictedLabels(Tree tree) {
        if (tree.isLeaf()) {
            return -1;
        }

        for (Tree child : tree.children()) {
            setPredictedLabels(child);
        }

        int newReturn = RNNCoreAnnotations.getPredictedClass(tree);
        tree.label().setValue(Integer.toString(newReturn));

        return newReturn;
  }

  private static void showValue(Tree treeChild, int deepNumChild){
        if ( treeChild.isLeaf() ){
            System.out.println("Valor ["+treeChild.value()+"] Prof: ["+deepNumChild+"] ");
        } else {
            deepNumChild++;
            for (Tree treeChildChild : treeChild.children()) {
                SentimentTreeValidator.showValue(treeChildChild, deepNumChild);
            }
        }
  }

 /* This method will validate recursively all the nodes of a tree. To be valide, a node might have 2 valid children
  * or it might be a preterminal node.
  */
  private static boolean validateTree(Tree tree, int i){
        if (tree.isLeaf()) {
            System.out.println("Line Number:["+i+
                                "] IsLeaf:["+tree.isLeaf()+
                                "]  Is Preterminal:["+tree.isPreTerminal()+
                                "]  TreeChildrenLenght:["+tree.children().length+"] ");

        } else if (tree.isPreTerminal()) {
            return true;
        } else if (tree.children().length == 1) {
            System.out.println("Line Number:["+i+"] IsLeaf:["+tree.isLeaf()+
                                "]  Is Preterminal:["+tree.isPreTerminal()+
                                "]  TreeChildrenLenght:["+tree.children().length+"] ");

        } else if (tree.children().length == 2) {
            boolean ret01 = SentimentTreeValidator.validateTree(tree.children()[0], i);
            boolean ret02 = SentimentTreeValidator.validateTree(tree.children()[1], i);

            if ( ret01 && ret02 ){
                return true;
            }
        } else {
            System.out.println("====================================================================================" +
                                "=======================================================");
            System.out.println("Line Number:["+i+
                                "] IsLeaf:["+tree.isLeaf()+
                                "]  Is Preterminal:["+tree.isPreTerminal()+
                                "]  TreeChildrenLenght:["+tree.children().length+"] ");
            System.out.println("====================================================================================" +
                                "=======================================================");
            
            int deepNumChild = 0;
            
            for (Tree treeChild : tree.children()) {
                SentimentTreeValidator.showValue(treeChild, deepNumChild);
            }
            System.out.println("====================================================================================" +
                                "=======================================================");
        }

        return false;
  }


  private static int updateSentimentFromMain(Tree contextTree, Tree mainTree, int lineNumber){

      Label label = contextTree.label();
      if (!(label instanceof CoreLabel)) {
          throw new IllegalArgumentException("Required a tree with CoreLabels");
      }
      CoreLabel cl = (CoreLabel) label;
      int phraseSentiment = new Integer(cl.value()).intValue();

      int resultSent = getSentimentFromMain(contextTree,phraseSentiment,mainTree,lineNumber);
      if (resultSent > -1)
          return resultSent;

      System.out.println("Phrase not found in the main:" + lineNumber);
      return phraseSentiment;
  }


  private static int getSentimentFromMain(Tree contextTree, int contextSentiment, Tree mainTree, int lineNumber) {
      if (mainTree.isLeaf()) {
            return -1;
      }

      String contextPTB = contextTree.toString();
      String mainPTB = mainTree.toString();

      if (contextPTB.length() < 4 || mainPTB.length() < 4){
          return -1;
      }

      contextPTB = contextPTB.replaceAll("\\([0-9] ","").replaceAll("\\)","").replaceAll(" ","");
      mainPTB = mainPTB.replaceAll("\\([0-9] ","").replaceAll("\\)","").replaceAll(" ","");

      if (contextPTB.equalsIgnoreCase(mainPTB) ){
          Label label = mainTree.label();
          if (!(label instanceof CoreLabel)) {
              throw new IllegalArgumentException("Required a tree with CoreLabels");
          }
          CoreLabel cl = (CoreLabel) label;
          int mainSentiment = new Integer(cl.value()).intValue();

          if( contextSentiment != mainSentiment ){
              System.out.println("Sentiment Change in the phrase :" + lineNumber +
                                 " OLD["+contextSentiment+
                                       "] NEW["+mainSentiment+"]");
              return mainSentiment;
          } else {
              return contextSentiment;
          }
      }

      for (Tree child : mainTree.children()) {
            int resultSent = getSentimentFromMain(contextTree,contextSentiment,child,lineNumber);
            if (resultSent > -1)
                return resultSent;
      }

      return -1;
  }

    /**
     * It will be fired to each line in the test dataset. It will use the 10th column as the PTB phrase to be analysed.
     * The 3rd column is used to denote if the phrase is a entire sentence (root sentence | mainTree) or is a simple
     * phrase.
     *
     * It will binarize the phrase, validate it and, in the case of it is not a main sentence, it will try to find the
     * correct Sentiment Score coming from the related main sentence.
     *
     *
     * @param lineCols
     * @param lineNumber
     * @param mainTree
     * @param outPsTest
     * @param binarizer
     * @param transformer
     * @param sentimentModel
     * @return
     */
  private static Tree processLine(String[] lineCols,
                                    int lineNumber,
                                    Tree mainTree,
                                    PrintStream outPsTest,
                                    TreeBinarizerLocal binarizer,
                                    CollapseUnaryTransformer transformer,
                                    SentimentModel sentimentModel){

        StringReader phraseReader = new StringReader(lineCols[9]);
        boolean isMain = (new Integer(lineCols[2]).intValue() == 1);

        MemoryTreebank treebank = new MemoryTreebank("utf-8");
        treebank.load(phraseReader);

        List<Tree> testTrees = new ArrayList<Tree>();
        for (Tree tree : treebank) {
            SentimentUtils.attachGoldLabels(tree);
            testTrees.add(tree);
        }

        Tree tree = testTrees.get(0);

        Tree testTree = tree.deepCopy();
        Tree binarized = binarizer.transformTree(testTree);
        Tree collapsedUnary = transformer.transformTree(binarized);

        Label label = tree.label();
        if (!(label instanceof CoreLabel)) {
            throw new IllegalArgumentException("Required a tree with CoreLabels");
        }
        CoreLabel cl = (CoreLabel) label;
        int phraseSentiment = new Integer(cl.value()).intValue();

        // if there is a sentiment model for use in prelabeling, we
        // label here and then use the user given labels to adjust
        if (sentimentModel != null) {
            Trees.convertToCoreLabels(collapsedUnary);
            SentimentCostAndGradient scorer = new SentimentCostAndGradient(sentimentModel, null);
            scorer.forwardPropagateTree(collapsedUnary);
            phraseSentiment = setPredictedLabels(collapsedUnary);
        }

        Trees.convertToCoreLabels(collapsedUnary);

        if (SentimentTreeValidator.validateTree(collapsedUnary, lineNumber)) {

            /* If this phrase is not the root sentence, we will try to get the sentiment score from the related root
             * sentence annotated tree (mainTree).
             * */
            if (!isMain && mainTree != null){
                phraseSentiment = updateSentimentFromMain(collapsedUnary,
                                                            mainTree,
                                                            new Integer(lineCols[0]).intValue());
            }

            String strPrint = "";
            strPrint += lineCols[0] +"\t";
            strPrint += lineCols[1] +"\t";
            strPrint += lineCols[2] +"\t";
            strPrint += lineCols[3] +"\t";
            strPrint += lineCols[4] +"\t";
            strPrint += lineCols[5] +"\t";
            strPrint += phraseSentiment +"\t";
            strPrint += lineCols[7] +"\t";
            strPrint += lineCols[8] +"\t";
            strPrint += collapsedUnary.toString() +"\t";

            outPsTest.println(strPrint);

            if ( isMain )
                return collapsedUnary;

        } else {
            System.out.println("Unable to VALIDATE the line number: " + lineNumber + " ISMAIN: "+isMain);
        }

        return null;
  }

  public static void main(String[] args) throws IOException {

        String trainPath = null;
        String devPath = null;
        String testPath = null;
        String prefix = null;

        String sentimentModelPath = null;
        SentimentModel sentimentModel = null;

        for (int argIndex = 0; argIndex < args.length; ) {
            if (args[argIndex].equalsIgnoreCase("-sentimentModel")) {
                sentimentModelPath = args[argIndex + 1];
                argIndex += 2;
            } else if (args[argIndex].equalsIgnoreCase("-trainpath")) {
                trainPath = args[argIndex + 1];
                argIndex += 2;
            } else if (args[argIndex].equalsIgnoreCase("-devpath")) {
                devPath = args[argIndex + 1];
                argIndex += 2;
            } else if (args[argIndex].equalsIgnoreCase("-testpath")) {
                testPath = args[argIndex + 1];
                argIndex += 2;
            } else if (args[argIndex].equalsIgnoreCase("-prefix")) {
                prefix = args[argIndex + 1];
                argIndex += 2;
            } else {
                argIndex++;
            }
        }

        CollapseUnaryTransformer transformer = new CollapseUnaryTransformer();
        String parserModel = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
        LexicalizedParser parser = LexicalizedParser.loadModel(parserModel);
        TreeBinarizerLocal binarizer = new TreeBinarizerLocal(parser.getTLPParams().headFinder(),
                                                                parser.treebankLanguagePack(),
                                                                false,
                                                                false,
                                                                0,
                                                                false,
                                                                false,
                                                                0.0,
                                                                false,
                                                                true,
                                                                false);


     /* If a trainPath is provided, the file is read and each line is checked and updated with a valid PTB format.
      */
      if (trainPath != null) {
            String trainPathOutput = trainPath.replaceFirst(prefix, "");


            System.out.println("Train File Path: " + trainPathOutput);

            List<Tree> trainingTrees = SentimentUtils.readTreesWithGoldLabels(trainPath);

            System.out.println("Read in " + trainingTrees.size() + " training trees");

            PrintStream outPsTrain = new PrintStream(new File(trainPathOutput));

            int i = 0;
            int deepNum = 1;
            for (Tree tree : trainingTrees) {
                Tree trainingTree = tree.deepCopy();
                Tree binarized = binarizer.transformTree(trainingTree);
                Tree collapsedUnary = transformer.transformTree(binarized);

                Trees.convertToCoreLabels(collapsedUnary);
                collapsedUnary.indexSpans();

                if (SentimentTreeValidator.validateTree(collapsedUnary, i)) {
                    outPsTrain.println(collapsedUnary);
                }

                i++;
            }

            outPsTrain.close();
        }

      /* If a devPath is provided, the file is read and each line is checked and updated with a valid PTB format.
       */
        if (devPath != null) {
            String devPathOutput = devPath.replaceFirst(prefix, "");
            PrintStream outPsDev = new PrintStream(new File(devPathOutput));

            System.out.println("Dev File Path: " + devPathOutput);

            List<Tree> devTrees = SentimentUtils.readTreesWithGoldLabels(devPath);

            System.out.println("Read in " + devTrees.size() + " dev trees");

            int i = 0;
            int deepNum = 1;
            for (Tree tree : devTrees) {
                Tree trainingTree = tree.deepCopy();
                Tree binarized = binarizer.transformTree(trainingTree);
                Tree collapsedUnary = transformer.transformTree(binarized);

                Trees.convertToCoreLabels(collapsedUnary);
                collapsedUnary.indexSpans();

                if (SentimentTreeValidator.validateTree(collapsedUnary, i)) {
                    outPsDev.println(collapsedUnary);
                }
                i++;
            }

            outPsDev.close();
        }


      /* If a Sentiment Model is set, it is charged to be used to annotate the sentiment score of each phrase.
       */
        if (sentimentModelPath != null) {
            sentimentModel = SentimentModel.loadSerialized(sentimentModelPath);
        }

      /* If the testPath is set, each line of the file is read, tested and annotated using the Sentiment Model indicated
       * above. Actually, it will use only the last column of each line as PTB phrase. The other columns are metadata
       * generated by the previous python processes. Some of them are used here (isMain), others don t
       *
       * It writes a file in the TSV format, keeping the metadata but updating it.
       */
        if (testPath != null) {
            String testPathOutput = testPath.replaceFirst(prefix, "");
            System.out.println("Test File Path: " + testPathOutput);
            PrintStream outPsTest = new PrintStream(new File(testPathOutput));

            BufferedReader reader = new BufferedReader(
                                                new InputStreamReader(
                                                    IOUtils.getInputStreamFromURLOrClasspathOrFileSystem(testPath),
                                                    "utf-8")
                                            );

            String headerOutput = "PhraseId";
            headerOutput += "\tSentenceId";
            headerOutput += "\tIsMain";
            headerOutput += "\tnumLeftParts";
            headerOutput += "\tleftParts";
            headerOutput += "\tPhrase";
            headerOutput += "\tSentiment";
            headerOutput += "\tnumWords";
            headerOutput += "\tnumChars";
            headerOutput += "\tPTBPhrase";

            outPsTest.println(headerOutput);
            int lineNumber = 1;
            reader.readLine();

            Tree mainTree = null;

            while (true) {
                lineNumber++;

                String line = reader.readLine();
                if (line == null) {
                    break;
                }

                line = line.trim();

                if (line.length() <= 0) {
                    continue;
                }

                String[] lineCols = line.split("\t");

                if (lineCols == null || lineCols.length < 10) {
                    System.out.println("Unable to read the line number: " + lineNumber);
                    continue;
                }

                Tree resultMainTree = processLine(lineCols,
                                                    lineNumber,
                                                    mainTree,
                                                    outPsTest,
                                                    binarizer,
                                                    transformer,
                                                    sentimentModel);

                if (resultMainTree != null){
                    mainTree = resultMainTree;
                }
            }

            outPsTest.close();
        }

   }
    
 
}
