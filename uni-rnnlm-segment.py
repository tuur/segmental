# Word Segmentation using Unidirectional RNNLM: Tuur, Kata, Stalin
import argparse
import subprocess
import sys
import os
import math
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Given a text file, and a prob-threshold trains a unidirectional RNNLM, and segments the text according to those places where the threshold is reached.')
    parser.add_argument('text', metavar='text', type=str,
                   help='The input text')
    parser.add_argument('-threshold', metavar='-threshold', type=float,default = 0.5,
                   help='The prob threshold (default=0.5)')
    parser.add_argument('-rnnlm', metavar='rnnlm', type=str, default='./rnnlm',
                   help='file path to the rnnlm program (default=./rnnlm)')
    parser.add_argument('-output', metavar='output', type=str, default='segmented.txt',
                   help='segmented output file (default: segmented.txt)')
    parser.add_argument('-fast', metavar='fast', type=int, default=1,
                   help='Runs each RNNLM only for one iteration, is faster, but the LM is less accurate.(default=1)')
    parser.add_argument('-hidden', metavar='hidden', type=int, default=50,
                   help='Number of nodes in the hidden layer of the RNNLMs (default=50)')

    args = parser.parse_args()  
    
    if not(os.path.isfile(args.rnnlm)):
        sys.stderr.write('ERROR: Please provide a valid rnnlm path (option: -rnnlm rnnlmFilePath)\n')
        exit()
     
    tmpFolder = args.output + '-tmp/' 
    
    if not(os.path.exists(tmpFolder)):
        os.makedirs(tmpFolder)
    else:
        shutil.rmtree(tmpFolder)
        os.makedirs(tmpFolder)    

     
    # Split text in training and development texts, for RNNLM
    sys.stderr.write('(1) Preparing for RNNLM training...\n')
    trainFile = open(tmpFolder + 'train.tmp', 'w')
    devFile = open(tmpFolder + 'dev.tmp','w')
    lineNr = 0
    vocab = set([])
    with open(args.text) as f: 
        for line in f.readlines():
            words = line.rstrip().split()
            vocab = vocab.union(set(words))
            if lineNr%5 == 0:
                devFile.write(line)
            else:
                trainFile.write(line)
            lineNr+=1
    trainFile.close()
    devFile.close()
    
    classSize = int(math.sqrt(len(vocab)))
    sys.stderr.write('Vocabulary:'+str(len(vocab))+'\n')
    sys.stderr.write('(2) Training RNNLM...\n')
    # Training RNNLM
    with open(tmpFolder + 'out.tmp','w') as output:
        command = [args.rnnlm,'-hidden', str(args.hidden),'-class', str(classSize), '-train', tmpFolder + 'train.tmp', '-valid',tmpFolder + 'dev.tmp','-rnnlm',tmpFolder + 'model.tmp','-test', args.text,'-debug','2']
        if args.fast:
            command += ['-one-iter']
        proc = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
    
    # Segmenting using output from RNNLM
    start = False
    firstword = True
    with open(args.output, 'w') as segmented:
        for line in iter(proc.stdout.readline,''):
                
                # if the training output part of stdout is over and it is actually outputting the probabilities
                if start: 
                    try:
                        count, prob, word = line.split()
                        prob = float(prob)
                    except:
                        sys.stderr.write(':'+line[:-1]+'\n')              
                    if word=='</s>':
                        segmented.write('\n')
                        firstword = True
                    else:
                        if prob > args.threshold or firstword:
                            segmented.write(word)
                            firstword = False
                        else:
                            segmented.write(' '+word)

                  

            
                if line=='----------------------------------\n': # last line of training output
                    sys.stderr.write('(3) Segmenting Text...\n')
                    start=True    
 
