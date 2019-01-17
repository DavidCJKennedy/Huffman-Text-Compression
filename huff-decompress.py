#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt,time
import pickle


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
        
        # If char in args then use char symbols,
        # A char being any character ie alphanumeric, space, newline etc
        if 'char' in args:
            self.symbolType = "char"
        else:
            # Else then use word symbols
            # Words being every continuous sequence of alphabetic character 
            # with punctuation, newlines etc treated as individual words
            self.symbolType = "word"
        
        self.file = args[0]
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
## MARK - Class to decompress the binary file and retrieve original text symbols

class DataDecompress:
    
## MARK - Initialisation Method to start file decompression   

    def __init__(self, symbolModel, compressedFile):
        self.convertToBinary(symbolModel, compressedFile)
        
## MARK - Method that converts a file of binary format to a string of bits
        
    def convertToBinary(self, symbolModel, compressedFile):
        # Declare a blank array to store the bitwise representaion of the .bin file
        decompressedData = []
        
        # Open the compressed text .bin file
        with open(compressedFile, 'rb') as file:
            # For each byte in the .bin file (1 byte = 8 bits)
            for byte in file.read():
                # Convert the byte value to binary. Fill empty bits so the bit strings
                # Are always 8 bits long. IE rather than 0x08 = 1000 fill empty bits 0x08 = 00001000
                # [2:] strips the binary identifier so only the bits remain 
                bits = str(bin(byte))[2:].zfill(8)
                # Append the bits for each byte to the decompressedData array
                decompressedData.append(bits)
        
        # Once each byte has been convert to bits, join each element in the array to create
        # one long binary string
        decompressedData = ''.join(map(str, decompressedData))
        
        # Call the decompression method to turn the binary back to symbols using the symbol model
        self.decompress(symbolModel, decompressedData)

## MARK - Method that completes the conversion of the binary string to the original text

    def decompress(self, symbolModel, data):
        # Declare an empty string to store the converted original text in
        text = ""
        # Declare an empty string to store the sections of binary data being individually decompressed
        code = ""
        # Flip the symbol model keys and values
        # New dictionary is dict = {binary representation : symbol}
        # Done for faster look up times and hence faster decompression times
        model = {v : k for k,v in symbolModel.items()}
        
        # Iterate through each bit in the binary string
        for bit in data:
            # Add the bit to the section of binary data currently being decompressed
            code += str(bit)
            if code in model:
                # If the binary code exists in the model then that section of code represents a valid symbol
                # Add the symbol to the text array and reset the code section variable
                text += model[code]
                code = ""
            else: # Else the section of code does not currently represent a symbol, so continue
                  # to add more bits to the code section from the compressed data
                continue
        
        # After the file has been decompressed into symbols 
        # Open the text file and write the text string
        file = open("infile-decompressed.txt", "w")
        file.write(text)
        file.close()


#==============================================================================
## MARK - Class to retrieve the symbol model from the .pkl file
                    
class SymbolModel:
    
# MARK - Initialisation Method to retrieve the symbol model from file using pickle
    
    def __init__(self, symbolModelFile):
        with open(symbolModelFile, 'rb') as model:
            self.symbolModel = pickle.load(model)


#==============================================================================
## MARK - Used to run the script from the commandline

if __name__ == '__main__':
    # Call the configuration class to assign key variables of the script file
    config = CommandLine()
    if config.exit:
        sys.exit(0)
    
    # Start the code timer
    t = CodeTimer()
    t.start('Decompressing')
    
    # Retrieve the symbol model
    symbolModel = SymbolModel('infile-symbol-model.pkl')
    # Decompress the .bin file using the retrieved symbol model
    decompress = DataDecompress(symbolModel.symbolModel, config.file)
    # Stop and print time as text file has been compressed  
    t.stopAndPrintTime('Decompressing')