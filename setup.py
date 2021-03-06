from setuptools import setup

setup(
    name='path_to_re',
    version='0.0.18',
    packages=['path_to_re', 'path_to_re.extra', 'path_to_re.internal', 'path_to_re.gcn', 'path_to_re.gcn.supplement', 'path_to_re.gcn.enhance'],
    url='https://github.com/yyellin/relation_extraction_utils',
    license='GPLv3',
    author='yyellin',
    author_email='yyellin@gmail.com',
    description='Various utilities for processing and analyzing relation extraction related data',
    install_requires=[
        'conllu', 'pytorch_pretrained_bert', 'jsonlines', 'docopt', 'more_itertools', 'stanfordnlp', 'nltk', 'pandas', 'networkx', 'spacy', 'tupa', 'ucca', 'requests', 'stanfordcorenlp', 'ijson'
    ]
)
