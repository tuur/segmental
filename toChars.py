import argparse
import codecs
import io

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Given a text, replaces all _ by -, spaces by _, and then separates all characters by a space.')
    parser.add_argument('text', metavar='text', type=str,
                   help='The input text')
    args = parser.parse_args()  
    
    out = args.text + '.chars'
    with io.open(out, 'w', encoding='utf-8') as out:
        with io.open(args.text, 'r', encoding= 'utf-8') as text:
            for line in text:
                line = line.rstrip().replace('_','-').replace(' ','_')
                out.write(u'<l>')
                for char in line:
                    out.write(u' '+char)
                out.write(u' </l>\n')
