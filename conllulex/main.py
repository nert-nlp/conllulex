import sys

import click

from conllulex import conllulex_enrichment
from conllulex.config import CORPUS_CFG
from conllulex.conllulex_to_json import convert_conllulex_to_json
from conllulex.govobj import govobj_enhance


@click.group()
def top():
    pass


@click.command(
    help="Take in an incomplete conllulex file, compute additional data for it, and "
    "write out the changes to the output path."
)
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--corpus",
    "-c",
    type=click.Choice(CORPUS_CFG.keys(), case_sensitive=False),
    help="The corpus contained in the conllulex file.",
    default="pastrie",
)
@click.option(
    "--subtasks",
    "-x",
    type=str,
    help="A comma-delimited list of subtasks to execute, regardless of the corpus configuration. "
    f"Possible values are: {', '.join(conllulex_enrichment.SUBTASKS.keys())}. See "
    f"conllulex_richment.py for more details.",
)
def enrich(input_path, output_path, corpus, subtasks):
    if subtasks is None:
        subtasks = CORPUS_CFG[corpus]["enrichment_subtasks"]
    else:
        subtasks = [s.strip() for s in subtasks.split(",")]
    conllulex_enrichment.main(input_path, output_path, subtasks)


@click.command(
    help="Read an input conllulex file, convert it into the JSON format,"
    " and write the result out to the output path. If there are validation errors, "
    "fail before writing anything and print errors out to stdout, like a compiler."
)
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--corpus",
    "-c",
    type=click.Choice(CORPUS_CFG.keys(), case_sensitive=False),
    help="The corpus contained in the conllulex file. ",
    default="pastrie",
)
@click.option(
    "--include-morph-head-deprel/--no-include-morph-head-deprel",
    default=True,
    help="Whether to include CoNLL-U MORPH, HEAD, DEPREL, and EDEPS columns, if available, in the output json. "
    "FORM, UPOS, XPOS and LEMMA are always included.",
)
@click.option(
    "--include-misc/--no-include-misc",
    default=True,
    help="Whether to include CoNLL-U MISC column, if available, in the output json.",
)
@click.option(
    "--validate-upos-lextag/--no-validate-upos-lextag",
    default=True,
    help="Whether to validate that UPOS and LEXTAG are compatible",
)
@click.option(
    "--validate-type/--no-validate-type",
    default=True,
    help="Whether to validate SWE-specific or SMWE-specific tags that only apply to the corresponding MWE type",
)
@click.option(
    "--store-conllulex-string",
    type=click.Choice(["none", "full", "toks"]),
    default="none",
    help="Set to full to include all conllulex input lines as a string in the returned JSON, "
    "or set to toks to exclude ellipsis tokens and metadata lines.",
)
@click.option(
    "--override-mwe-render/--no-override-mwe-render",
    default=False,
    help="When not set to true, compare the given `# mwe = ...` metadata to an automatically"
    "generated version and report an error if there is a mismatch. Otherwise, silently override.",
)
def conllulex2json(
    input_path,
    output_path,
    corpus,
    include_morph_head_deprel,
    include_misc,
    validate_upos_lextag,
    validate_type,
    store_conllulex_string,
    override_mwe_render,
):
    convert_conllulex_to_json(
        input_path=input_path,
        output_path=output_path,
        corpus=corpus,
        include_morph_deps=include_morph_head_deprel,
        include_misc=include_misc,
        validate_upos_lextag=validate_upos_lextag,
        validate_type=validate_type,
        store_conllulex_string=store_conllulex_string,
        override_mwe_render=override_mwe_render,
    )


def conllulex2json_hindi():
    sys.argv.insert(1, "conllulex2json")
    sys.argv.insert(2, "--corpus")
    sys.argv.insert(3, "hindi")
    top()


def conllulex2json_streusle():
    sys.argv.insert(1, "conllulex2json")
    sys.argv.insert(2, "--corpus")
    sys.argv.insert(3, "streusle")
    top()


def conllulex2json_pastrie():
    sys.argv.insert(1, "conllulex2json")
    sys.argv.insert(2, "--corpus")
    sys.argv.insert(3, "pastrie")
    top()


@click.command(
    help="Extend JSON file with govobj information."
)
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--edeps/--no-edeps",
    help="Whether the corpus has enhanced dependencies available or not.",
    default=True
)
def govobj(input_path, output_path, edeps):
    govobj_enhance(input_path, output_path, edeps)


top.add_command(enrich)
top.add_command(conllulex2json)
top.add_command(govobj)

if __name__ == "__main__":
    top()
