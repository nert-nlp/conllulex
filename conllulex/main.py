import sys
from collections import defaultdict

import click

from conllulex import conllulex_enrichment
from conllulex.config import CORPUS_CFG
from conllulex.conllulex_to_json import convert_conllulex_to_json
from conllulex.govobj import govobj_enhance


@click.group()
def top():
    pass


def _layer_by_name(layers, name):
    for x in layers:
        if x["name"] == name:
            return x
    return None


@click.command(help="Take a Glam import (github.com/lgessler/glam) and format it as CoNLL-U-Lex")
@click.argument("input-filepath")
@click.argument("output-filepath")
@click.option("--text-layer-name", default="Text")
@click.option("--token-layer-name", default="Tokens")
@click.option("--ss1-layer-name", default="Scene Role")
@click.option("--ss2-layer-name", default="Function")
@click.option("--translation-layer-name", default="Translation")
def glam2conllulex(
    input_filepath,
    output_filepath,
    text_layer_name,
    token_layer_name,
    ss1_layer_name,
    ss2_layer_name,
    translation_layer_name,
):
    import json

    with open(input_filepath, "r") as f:
        d = json.load(f)
    doc_name = d["name"].replace(" ", "-").lower()
    text_layer = _layer_by_name(d["text-layers"], text_layer_name)
    token_layer = _layer_by_name(text_layer["token-layers"], token_layer_name)
    ss1_layer = _layer_by_name(token_layer["span-layers"], ss1_layer_name)
    ss2_layer = _layer_by_name(token_layer["span-layers"], ss2_layer_name)
    translation_layer = _layer_by_name(token_layer["span-layers"], translation_layer_name)

    text = text_layer["text"]["body"]
    text_lines = text.split("\n")
    tokens = sorted([t for t in token_layer["tokens"]], key=lambda t: t["begin"])
    ss1_spans = {s["tokens"][0]["id"]: s for s in ss1_layer["spans"] if s["value"] != ""}
    ss2_spans = {s["tokens"][0]["id"]: s for s in ss2_layer["spans"] if s["value"] != ""}
    translation_spans = {s["tokens"][0]["id"]: s for s in translation_layer["spans"] if s["value"] != ""}

    # Begin constructing token-span bundles
    tokens_by_sentence = defaultdict(list)
    token_to_sentence = {}
    translations = defaultdict(list)
    for token in tokens:
        if token["value"].strip() == "":
            continue
        s_index = text[: token["begin"]].count("\n")
        tid = token["id"]
        token["ss1"] = ss1_spans[tid]["value"] if tid in ss1_spans and ss1_spans[tid]["value"] != "" else None
        token["ss2"] = ss2_spans[tid]["value"] if tid in ss2_spans and ss2_spans[tid]["value"] != "" else None
        tokens_by_sentence[s_index].append(token)
        token_to_sentence[tid] = s_index
    for tid, translation_span in translation_spans.items():
        s_index = token_to_sentence[tid]
        translations[s_index] = translation_span["value"]

    outlines = []
    outlines.append(f"# newdoc id = {doc_name}")
    for s_index, tokens in tokens_by_sentence.items():
        outlines.append(f"# sent_id = {doc_name}-{s_index + 1}")
        outlines.append(f"# text = {text_lines[s_index]}")
        outlines.append(f"# translation = {translations[s_index]}")
        for i, token in enumerate(tokens):
            cols = ["_"] * 19
            cols[0] = f"{i + 1}"
            cols[1] = f"{token['value']}"
            if token["ss1"] is not None:
                cols[13] = token["ss1"]
            if token["ss2"] is not None:
                cols[14] = token["ss2"]
            outlines.append("\t".join(cols))
        outlines.append("")

    with open(output_filepath, "w") as f:
        f.write(("\n".join(outlines)) + "\n")


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
    help="When not set to true, compare the given `# mwe = ...` metadata to an automatically "
    "generated version and report an error if there is a mismatch. Otherwise, silently override.",
)
@click.option(
    "--force-write/--no-force-write",
    default=False,
    help="By default, the conversion will halt if any errors are detected. If this option is set to true, "
    "print validation errors as warnings and produce output anyway.",
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
    force_write,
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
        force_write=force_write,
    )


@click.command(help="Extend JSON file with govobj information.")
@click.argument("input_path")
@click.argument("output_path")
@click.option("--edeps/--no-edeps", help="Whether the corpus has enhanced dependencies available or not.", default=True)
def govobj(input_path, output_path, edeps):
    govobj_enhance(input_path, output_path, edeps)


top.add_command(glam2conllulex)
top.add_command(enrich)
top.add_command(conllulex2json)
top.add_command(govobj)

if __name__ == "__main__":
    top()
