"""Enhance TAC with all UCCA stuff using UCCA tokenization

Usage:
  enhance_tac3.py <tupa_module_path>  [--input=<input-file>] [--output=<output-file>]
  enhance_tac3.py (-h | --help)

Options:
  -h --help     Show this screen.
"""
import sys
import ijson
import jsonlines

from docopt import docopt

from path_to_re.internal.sanitize_tacred import SanitizeTacred
from path_to_re.internal.map_tokenization import MapTokenization
from path_to_re.internal.pipe_error_work_around import revert_to_default_behaviour_on_sigpipe
from path_to_re.internal.tupa_parser import TupaParser

from path_to_re.gcn.enhance.ucca_path import UccaPath
from path_to_re.gcn.enhance.ucca_encodings_min_subtree import UccaEncodingMinSubtree
from path_to_re.gcn.enhance.ucca_heads import UccaHeads
from path_to_re.gcn.enhance.ucca_distances_from_path import UccaDistancesFromPath
from path_to_re.gcn.enhance.ucca_encodings import UccaEncoding


def enhance_tac3(input_stream, output_stream, model_prefix):

    json_read = ijson.items(input_stream, 'item')

    with jsonlines.Writer(output_stream) as json_write:

        parser = TupaParser(model_prefix)

        for item in json_read:
            sentence = ' '.join(SanitizeTacred.sanitize_tokens(item['token']))
            parsed_sentence = parser.parse_sentence(sentence)
            if parsed_sentence is None:
                print('failed to perform UCCA parse')
                continue

            sanitized_tac_tokens = SanitizeTacred.sanitize_tokens(item['token'])
            ucca_tokens = [ucca_terminal.text for ucca_terminal in parsed_sentence.terminals]
            tac_to_ucca = MapTokenization.map_a_to_b(sanitized_tac_tokens, ucca_tokens)

            #ensure tac_to_ucca is 'surjective' over 'ucca_tokens' and defined over 'sanitized_tac_tokens':
            if not MapTokenization.check_surjectivity(tac_to_ucca, ucca_tokens) \
                    or not MapTokenization.check_defined(tac_to_ucca, sanitized_tac_tokens):
                print('failed to align all UCCA and TACRED tokens for UCCA head/dep extraction')
                continue

            item['tac_to_ucca'] = tac_to_ucca
            item['ucca_tokens'] = ucca_tokens

            item['spacy_tag'] = [ucca_terminal.tag for ucca_terminal in parsed_sentence.terminals]
            item['spacy_pos'] = [ucca_terminal.pos for ucca_terminal in parsed_sentence.terminals]
            item['spacy_ent'] = [ucca_terminal.ent for ucca_terminal in parsed_sentence.terminals]
            item['spacy_head'] = [ucca_terminal.head for ucca_terminal in parsed_sentence.terminals]

            for enhancer in [ UccaPath(), UccaEncodingMinSubtree(), UccaHeads(), UccaDistancesFromPath(), UccaEncoding() ]:
                for enhancement_key, enhancement_value in enhancer.enhance(item, tac_to_ucca, parsed_sentence).items():
                        item[enhancement_key] = enhancement_value

            json_write.write(item)


if __name__ == "__main__":
    args = docopt(__doc__)

    input_stream = open(args['--input'], encoding='utf-8') if args['--input'] is not None else sys.stdin
    output_stream = open(args['--output'], 'w', encoding='utf-8', newline='', buffering=1) if args['--output'] is not None else sys.stdout
    tupa_module_path = args.get('<tupa_module_path>', None)

    # https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python
    revert_to_default_behaviour_on_sigpipe()

    enhance_tac3(input_stream, output_stream, tupa_module_path)

