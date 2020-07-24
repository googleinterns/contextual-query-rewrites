import os
import json
import sys
import json

sys.path.append('./../../utils/')
sys.path.append('./models/utils/')
import preprocess_translate_data as preprocess
import translate_utils as translate

def main(argv):
    """
    translates and writes the input data into 
    the wikisplit/wikifuse format, to be fed to 
    the lasertagger model
    """

    file = open(argv[1], 'r')
    outfile = open(argv[1].split('.')[0] + '_translated.tsv', 'w')
        
    with open("config.json") as json_file:
        config = json.load(json_file)

    for line in file.readlines():
        line = line.strip()
        if line != "":
            try:
                translated = translate.translate_text(
                    line,
                    src_lang="hi",
                    dst_lang="en",
                    project_id=config["ProjectID"])
                line1, line2 = translated.replace('.', ' . ') \
                                .replace('?', ' ? ').split('<::::>')
                outfile.write('. \t {0} <::::> {1} \n'.format(line1, line2))
            except Exception as e:
                print("failed", e, line)

    outfile.close()
    file.close()

if __name__ == '__main__':
    main(sys.argv)