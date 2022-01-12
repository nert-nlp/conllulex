# Introduction

This is a port of some of the [CoNLL-U-Lex](https://github.com/nert-nlp/streusle/blob/master/CONLLULEX.md) utils from [STREUSLE](https://github.com/nert-nlp/streusle). 

# Setup

Clone to a local repository and pip install:

```
git clone https://github.com/nert-nlp/conllulex.git
cd conllulex
pip install -e .
```

Alternatively, if you do not expect that you will need to make changes to the code in `conllulex`,
simply install via pip:

```
pip install git+https://github.com/nert-nlp/conllulex.git
```

# Usage

You will now have the following commands on your path:

```
conllulex-enrich
conllulex2json
conllulex-govobj
```

You may invoke any of these commands with `--help` to see options.

Any changes you make to your local copy of the code will automatically
be accounted for when you run these commands. You do **not** need to re-run
`pip install -e .`.

## CoNLL-U-Lex enrichment
This takes a minimal `.conllulex` file and adds and corrects information. Refer to
[`conllulex_enrichment.py`](./conllulex/conllulex_enrichment.py) for details, and
configure the steps for your corpus under the `enrichment_subtasks` key.

Example invocation:

```
conllulex-enrich --corpus hindi hindi.conllulex hindi_enriched.conllulex
```

## CoNLL-U-Lex to JSON conversion
This converts a `.conllulex` file into the JSON format originally used by STREUSLE.
If any validation errors are encountered, the program will report all errors and quit
without writing any output. There are many options for this command--see `--help`.

```
conllulex2json --corpus pastrie pastrie.conllulex pastrie.json
```

## Governor/Object information
A JSON can be enriched with governor/object information. Be sure no pass `--no-edeps`
or `--edeps` depending on if your corpus has enhanced dependencies:

```
conllulex-govobj --edeps streusle.json streusle.govobj.json
conllulex-govobj --no-edeps pastrie.json pastrie.govobj.json
```

# Configuring Languages and Corpora

There are language- and corpus-specific settings that may be configured in
[`config.py`](./conllulex/config.py).
If you are adding a new corpus or language, it is likely that you will need to change
this config. Note that all keys are mandatory, even if the value is empty.
