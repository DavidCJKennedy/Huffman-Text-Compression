#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter
from operator import attrgetter
import sys, getopt,time
import array
import pickle
import re


#==============================================================================
## MARK - Class to handle the initialisation of the script in commandline

class CommandLine: 
    
## MARK - Initialisation method, set class variables to those inputted from commandline
    
    def __init__(self):
        # Retrieve commandline arguments 
        opts, args = getopt.getopt(sys.argv[1:], 'hspw:o:')
        opts = dict(opts)
        self.exit = True
        
        # Check that arguments are valid
        if len(args) == 0:
            print("ERROR: Must specify symbol type: Options are -s char or -s word")
            return
        
        # If char in args then use char symbols
        # A char being any character alphanumeric, space, newline etc
        if 'char' in args:
            self.symbolType = "char"
        else: 
            # Else then use word symbols
            # Words being every continuous sequence of alphabetic character 
            # with punctuation, newlines etc treated as individual words
            self.symbolType = "word"
        
        self.file = args[1]
        self.exit = False


#==============================================================================
## MARK - Class to time the running of the script

class CodeTimer:
    
## MARK - Initialisation Method to start the timer
    
    def __init__(self):
        self.startTime = {}

## MARK - Method to start the timer when required and assign timer a label to represent process

    def start(self, label = None):
        self.startTime[label] = time.clock()
        
## MARK - Method to stop the timer and print resultant rounded time

    def stopAndPrintTime(self, label = None):
        # The time taken for the scipt to run is equal to 
        # time when stop method called - start time
        duration = time.clock() - self.startTime[label]
        # Print to console the time rounded to 2dp
        message = 'TIME (%s): %.2f' % (label, duration)
        print(message, file = sys.stderr)


#==============================================================================
## MARK - Class to generate the symbol model using the symbol type specified

class Tokeniser:
    
## MARK - Initialisation Method to set class variables and begin tokenisation
    
    def __init__(self, symbolType, inputFile):
        self.symbolType = symbolType
        self.inputFile = inputFile
        
        # Using a seperate method and local variables to generate model is faster than doing tokenisation 
        # in the init mdethod and using global variables
        self.generateModel(self.symbolType, self.inputFile)

## MARK - Method to generate the symbol model

    def generateModel(self, symbolType, inputFile):
        # Declare the model as a blank dictionary. model = {symbol: count}
        # Dictionaries are more efficient for symbol model as the look up speed is s(n) where n is number of elements
        model = {} 
        symbolCount = 0 # Start the total file symbol count
            
        if symbolType == "char": # Generate symbol model with characters as symbols
            with open(inputFile) as file: # Open the inputted file
                for line in file: # Iterate through each line in file
                    for character in line: # Iterate through each character in line
                        if character in model: # If the character already exists in the symbol model
                            model[character] = model[character] + 1 # Add one to character count
                            symbolCount = symbolCount + 1 # Add one to total symbol count
                        else: # New character found so add as new entry to symbol model dictionary
                            model[character] = 1
                            symbolCount = symbolCount + 1
               
        else: # Generate symbol model with words as symbols
            with open(inputFile) as file:
                for line in file: # Iterate through each line in file 
                    # Seach the line to find all elements that agree to the regex expression 
                    # Search returns an array of words and punctuation and newlines etc
                    # Regex allows whole words, punctuation, newlines and whitespace
                    for item in re.findall(r"[\w]+|[^\s\w]+|[\n\r\s]", line): 
                        if item in model:
                            model[item] = model[item] + 1
                            symbolCount = symbolCount + 1
                        else:
                            model[item] = 1
                            symbolCount = symbolCount + 1
            
        # Sort the symbol model in order of symbol count
        # For each symbol divide the count by the total symbol count for the text
        # This returns the rounded probability to 6dp for each symbol
        # symbolModel = {symbol: probability}
        # Using comprehensions, itemgetter and reverse = True as an argument rather than .reverse improves efficiency of sorting
        self.symbolModel = [(k, round((v / symbolCount), 6)) for k,v in sorted(model.items(), key = itemgetter(1), reverse = True)]
   
     
#==============================================================================
## MARK - Class to generate the huffman tree from the symbol model
        
class HuffmanTree:
    # Declare a dictionary for the symbol codes: codes = {symbol: binary representation}
    codes = {}
    
## MARK - Initialisation Method to seed the initial tree, each symbol in the symbol model is represented by a leaf node 
    
    def __init__(self, model):
        # For each item in the symbol model, convert the symbol to a leaf node and store nodes in the tree array
        self.tree = [Node(item[1], True, item[0]) for item in model]            
        self.buildTree(self.tree)
        
## MARK - Method to build the layered Huffman tree from the initial seed tree of leaf nodes
        
    def buildTree(self, seedTree):
        tree = seedTree
        
        # If the tree has more than one node, the root of the tree has not yet been reached
        # Hence further node combination is required to reach the root node
        while len(tree) > 1:
            # Sort the nodes of the tree by their probability 
            tree = sorted(tree, key = attrgetter('prob'), reverse = True)
            # Remove the last two elements from the array and assign to a new variable
            # These two variables represent the least two probable nodes in the tree
            node1 = tree.pop()
            node2 = tree.pop()
            # Create a new node from the least two probable nodes
            # The probability of the new node is the sum of the two branch nodes
            # The new node is not a leaf node as it has two branches
            # The left branch being node1 and the right branch being node2
            newNode = Node(round(node1.prob + node2.prob, 6), isLeafNode = False, leftBranch = node1, rightBranch = node2)
            # Add the new node to the tree and continue the while loop
            tree.extend([newNode])

        # If the tree has one node, the root, then get get the huffman codes
        self.getHuffmanCodes(tree[0], None)

## MARK - Method to traverse the Huffman tree and gather symbol codes, multiple
##        instances of this method will be called to traverse the full tree

    def getHuffmanCodes(self, tree, code):
        # If code is initially None then assign a new array to begin the code
        # Code is none when method is first called, the code array stores the path
        # taken to reach each symbol in the huffman tree
        if code == None:
            code = []
        
        # If the node, initially the root, has a left branch then travel down this branch
        if tree.left != None:
            # Every left branch has a 0 binary representation so add 0 to the code path array
            leftCode = code + [0]
            # Call this same method again to continue down the left node branch
            self.getHuffmanCodes(tree.left, leftCode)
        else:
            # A leaf node, that contains a symbol has no left or right branch
            # Hence add the binary code for the symbol the the symbol codes array
            # Each symbol code element is first joined to make one string element
            self.codes[tree.symbol] = ''.join(map(str, code))

        # In a seperate if statement, if the same node, initially the root, has a right branch
        # travel down this branch
        if tree.right != None:
            # Every right branch has a 1 binary representation so add a 1 to the code path array
            rightCode = code + [1]
            # Call this same method again to continue down the right node branch
            self.getHuffmanCodes(tree.right, rightCode)
            
            
#==============================================================================
## MARK - Class to compress the input text file using the calculated Huffman codes

class DataCompression:
    
## MARK - Initialisation Method to gather huffman codes variable and start text compression
    
    def __init__(self, inputFile, codes, symbolType):
        self.codes = codes
        self.compression(inputFile, codes, symbolType)
        
## MARK - Method to compress the text, requires the original text file, the huffman codes
##        and the symbolType used to generate the symbol model 

    def compression(self, inputFile, codes, symbolType):
        # Declare a blank array to store the binary representation of each word/char in the text
        compressedData = []
        # Declare an array of bytes
        binaryData = array.array('B')
        
        # Encode text via the symbol type
        if symbolType == "char":
            # Open the text file
            with open(inputFile) as file:
                # Iterate through each line of file
                for line in file:
                    # Iterate through each character as char mode selected
                    for character in line:
                        # Find the character binary representation and append to binary array
                        compressedData.extend(codes[character])
                        
        else: # Else encode text via words
            with open(inputFile) as file:
                for line in file:
                    # Same regex is used as when symbol model is created
                    # Regex allows whole words, punctuation, newlines and whitespace
                    for item in re.findall(r"[\w]+|[^\s\w]+|[\n\r\s]", line):
                         # Find the word binary representation and append to binary array
                        compressedData.extend(codes[item])
        
        # Combined multiple lines of code into one to improve coding efficiency
        # Iterate through the compressed binary representation array in chunks of 8 bits
        # Convert this chunk of 8 bits into binary and add to array 
        
        for byte in [int(''.join(map(str, compressedData[i:i + 8])), 2) for i in range(0, len(compressedData), 8)]:
            binaryData.append(byte)
            
        # Open the infile.bin which stores the compressed data
        # Add the bytes to the file
        f = open('infile.bin', 'wb')
        binaryData.tofile(f)
        f.close
        
        # Open the file to store the symbol model 
        # Use pickle to dump the symbol model dictionary to the file
        nf = open('infile-symbol-model.pkl', 'wb')
        pickle.dump(self.codes, nf, protocol = pickle.HIGHEST_PROTOCOL)     
        nf.close
        
        
#==============================================================================
## MARK - Class whose instances serve as the nodes for the Huffman tree
        
class Node:

    # Attributes are the left branch, right branch, the node probability
    # the symbol represented by the node if the node is a leaf
    left = None
    right = None
    prob = None
    symbol = None
    leafNode = None
    
## MARK - Initialisation Method to assign class attributes
    
    def __init__(self, probability, isLeafNode, symbol = None, leftBranch = None, rightBranch = None):
        self.left = leftBranch
        self.right = rightBranch
        self.prob = probability
        self.symbol = symbol
        self.leafNode = isLeafNode
        
        
#==============================================================================
## MARK - Used to run the script from the commandline
        
if __name__ == '__main__':
    # Call the configuration class to assign key variables of the script file
    config = CommandLine()
    if config.exit:
        sys.exit(0)
    
    # Start the code timer
    t = CodeTimer()
    t.start('SymbolModel')
    
    # Start the tokeniser
    tokeniser = Tokeniser(config.symbolType, config.file)
    
    
    # Generate the huffman tree with the symbol model generated in the tokeniser class
    huffmanTree = HuffmanTree(tokeniser.symbolModel)
    t.stopAndPrintTime('SymbolModel')
    t.start('Encoding')
    # Compress the text folder using codes generated in huffman tree class 
    encode = DataCompression(config.file, huffmanTree.codes, config.symbolType)
    # Stop and print time as text file has been compressed
    t.stopAndPrintTime('Encoding')
    