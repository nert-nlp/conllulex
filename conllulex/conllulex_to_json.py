import json
import re
from collections import defaultdict
from itertools import chain
from pprint import pprint, pformat
from typing import Iterable

from conllu.serializer import serialize_field

from conllulex.reading import get_conllulex_tokenlists


def _append_if_error(errors, sentence_id, test, explanation, token=None):
    """
    If a test fails, append an error/warning dictionary to errors.

    Args:
        errors: a list of errors or warnings
        sentence_id: ID of the sentence this applies to
        test: boolean from a checked expression
        explanation: user-friendly string explaining the error found by the flag

    Returns: the value of `flag`
    """
    if not test:
        errors.append({"sentence_id": sentence_id, "explanation": explanation, "token": token})
    return test


def _load_json(input_path, ss_mapper, include_morph_head_deprel, include_misc):
    errors = []
    warnings = []
    modified_sentences = []

    with open(input_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)
    for sentence in sentences:
        for lex_expr in chain(sentence["swes"].values(), sentence["smwes"].values()):
            if lex_expr["ss"] is not None:
                lex_expr["ss"] = ss_mapper(lex_expr["ss"])
            if lex_expr["ss2"] is not None:
                lex_expr["ss2"] = ss_mapper(lex_expr["ss2"])
            _append_if_error(
                errors,
                sentence["sent_id"],
                all(t > 0 for t in lex_expr["toknums"]),
                f"Token offsets must be positive, but this expression has non-positive ones: {lex_expr}",
            )

        if "wmwes" in sentence:
            for lex_expr in sentence["wmwes"].values():
                _append_if_error(
                    errors,
                    sentence["sent_id"],
                    all(t > 0 for t in lex_expr["toknums"]),
                    f"Token offsets must be positive, but this expression has non-positive ones: {lex_expr}",
                )

        if not include_morph_head_deprel:
            for token in sentence["toks"]:
                token.pop("feats", None)
                token.pop("head", None)
                token.pop("deprel", None)
                token.pop("edeps", None)

        if not include_misc:
            for token in sentence["toks"]:
                token.pop("misc", None)

        modified_sentences.append(sentence)

    return modified_sentences, errors, warnings


def _store_conllulex(sentence, token_list, errors, warnings, store_conllulex_string):
    sentence_lines = token_list.serialize()
    if store_conllulex_string == "none":
        return
    elif store_conllulex_string == "full":
        sentence["conllulex"] = token_list.serialize()
    elif store_conllulex_string == "toks":
        sentence_lines = [
            line for line in sentence_lines.split("\n") if line[0] != "#" and "." not in line.split("\t")[0]
        ]
        sentence["conllulex"] = "\n".join(sentence_lines)


def _store_metadata(sentence, token_list, errors, warnings):
    banned_keys = ["toks", "swes", "smwes", "wmwes"]
    metadata = token_list.metadata
    _append_if_error(
        errors,
        sentence["sent_id"],
        all(k not in metadata for k in banned_keys),
        '"toks", "swes", "smwes", and "wmwes" are not allowed to be metadata keys',
    )
    for k, v in metadata.items():
        if k not in banned_keys and not any(skip in k for skip in ["newpar", "newdoc", "TODO"]):
            sentence[k] = v


def _store_morph_and_deps(token_dict, token, errors, warnings, is_ellipsis, is_supertoken, sent_id):
    token_dict["feats"] = serialize_field(token["feats"])
    token_dict["head"] = token["head"]
    token_dict["deprel"] = token["deprel"]
    token_dict["edeps"] = serialize_field(token["deps"])

    if token["head"] == "_":
        _append_if_error(
            errors,
            sent_id,
            is_ellipsis or is_supertoken,
            f"Only ellipsis tokens and supertokens are allowed to not have a head.",
            token=token
        )
        token_dict["head"] = None
    if token["deprel"] == "_":
        _append_if_error(
            errors,
            sent_id,
            is_ellipsis or is_supertoken,
            f"Only ellipsis tokens and supertokens are allowed to not have a deprel",
            token=token
        )
        token_dict["deprel"] = None


def _store_conllulex_columns(sentence, token_dict, token, errors, warnings, ss_mapper):
    sent_id = sentence["sent_id"]
    token_num = token_dict["#"]

    if token["smwe"] != "_":
        smwe_group, smwe_position = list(map(int, token["smwe"].split(":")))
        token_dict["smwe"] = (smwe_group, smwe_position)
        sentence["smwes"][smwe_group]["toknums"].append(token_num)
        _append_if_error(
            errors,
            sent_id,
            sentence["smwes"][smwe_group]["toknums"].index(token_num) == smwe_position - 1,
            f"SMWE tokens must have positions labeled in strictly increasing order, "
            f"but an out-of-order indexing exists.",
            token=token
        )
        if smwe_position == 1:
            _append_if_error(
                errors,
                sent_id,
                " " in token["lexlemma"],
                f"Token is the beginning of a SMWE, but lexlemma doesn't appear to have multiple tokens in it. ",
                token=token
            )
            sentence["smwes"][smwe_group]["lexlemma"] = token["lexlemma"]
            _append_if_error(
                errors, sent_id, token["lexcat"] != "_", f"SMWE token lacks a lexcat. ", token=token
            )
            sentence["smwes"][smwe_group]["lexcat"] = token["lexcat"]
            sentence["smwes"][smwe_group]["ss"] = ss_mapper(token["ss"]) if token["ss"] != "_" else None
            sentence["smwes"][smwe_group]["ss2"] = ss_mapper(token["ss2"]) if token["ss2"] != "_" else None
        else:
            _append_if_error(
                errors,
                sent_id,
                token["lexlemma"] == "_",
                f"Non-initial tokens in SMWEs should always have lexlemma '_'.",
                token=token
            )
            _append_if_error(
                errors,
                sent_id,
                token["lexcat"] == "_",
                f"Non-initial tokens in SMWEs should always have lexcat '_'.",
                token=token
            )
    else:
        token_dict["smwe"] = None
        _append_if_error(
            errors,
            sent_id,
            token["lexlemma"] == token["lemma"],
            f"Single-word expression lemma \"{token['lexlemma']}\" doesn't match token lemma \"{token['lemma']}\"",
            token=token
        )
        sentence["swes"][token_num]["lexlemma"] = token["lexlemma"]
        _append_if_error(errors, sent_id, token["lexcat"] != "_", f"SWE token must have lexcat.", token=token)
        sentence["swes"][token_num]["lexcat"] = token["lexcat"]
        sentence["swes"][token_num]["ss"] = ss_mapper(token["ss"]) if token["ss"] != "_" else None
        sentence["swes"][token_num]["ss2"] = ss_mapper(token["ss2"]) if token["ss2"] != "_" else None
        sentence["swes"][token_num]["toknums"] = [token_num]

    if token["wmwe"] != "_":
        wmwe_group, wmwe_position = list(map(int, token["wmwe"].split(":")))
        token_dict["wmwe"] = (wmwe_group, wmwe_position)
        sentence["wmwes"][wmwe_group]["toknums"].append(token_num)
        _append_if_error(
            errors,
            sent_id,
            sentence["wmwes"][wmwe_group]["toknums"].index(token_num) == wmwe_position - 1,
            f"WMWE tokens must have positions labeled in strictly increasing order, "
            f"but an out-of-order indexing exists.",
            token=token
        )
        if wmwe_position == 1:
            _append_if_error(
                errors, sent_id, token["wlemma"] != "_", f"Beginning of a WMWE must have a wlemma.", token=token
            )
            sentence["wmwes"][wmwe_group]["lexlemma"] = token["wlemma"]
            # _append_if_error(errors, sent_id, token["wcat"] != "_", f"WMWE token lacks a wcat.", token=token)
            sentence["wmwes"][wmwe_group]["lexcat"] = token["wcat"] if token["wcat"] != "_" else None
        else:
            _append_if_error(
                errors,
                sent_id,
                token["wlemma"] == "_",
                f"Non-initial tokens in WMWEs should always have lexlemma '_'.",
                token=token
            )
            _append_if_error(
                errors,
                sent_id,
                token["wcat"] == "_",
                f"Non-initial tokens in SMWEs should always have wcat '_'.",
                token=token
            )
    else:
        token_dict["wmwe"] = None
        _append_if_error(
            errors,
            sent_id,
            token["wlemma"] == "_",
            f"wlemma should be _ if token does not belong to WMWE, but token has wlemma value: {token['wlemma']}",
            token=token
        )
        _append_if_error(
            errors,
            sent_id,
            token["wcat"] == "_",
            f"wcat should be _ if token does not belong to WMWE, but token has wcat value: {token['wcat']}",
            token=token
        )

    lextag = token["lextag"]
    for m in re.finditer(r"\b[a-z]\.[A-Za-z/-]+", token["lextag"]):
        lextag = lextag.replace(m.group(0), ss_mapper(m.group(0)))
    for m in re.finditer(r"\b([a-z]\.[A-Za-z/-]+)\|\1\b", lextag):
        # e.g. p.Locus|p.Locus due to abstraction of p.Goal|p.Locus
        lextag = lextag.replace(m.group(0), m.group(1))  # simplify to p.Locus
    token_dict["lextag"] = lextag


def _load_sentences(
    input_path,
    include_morph_deps,
    include_misc,
    validate_upos_lextag,
    validate_type,
    store_conllulex_string,
    override_mwe_render,
    ss_mapper,
):
    errors = []
    warnings = []
    sentences = []
    if input_path.endswith(".json"):
        return _load_json(input_path, ss_mapper, include_morph_deps, include_misc)

    for token_list in get_conllulex_tokenlists(input_path):
        sent_id = token_list.metadata["sent_id"]
        sentence = {
            "sent_id": sent_id,
        }
        _store_metadata(sentence, token_list, errors, warnings)
        sentence.update(
            {
                "toks": [],  # excludes ellipsis tokens, to make indexing convenient
                "etoks": [],  # ellipsis tokens only
                "swes": defaultdict(
                    lambda: {
                        "lexlemma": None,
                        "lexcat": None,
                        "ss": None,
                        "ss2": None,
                        "toknums": [],
                    }
                ),
                "smwes": defaultdict(
                    lambda: {
                        "lexlemma": None,
                        "lexcat": None,
                        "ss": None,
                        "ss2": None,
                        "toknums": [],
                    }
                ),
                "wmwes": defaultdict(lambda: {"lexlemma": None, "toknums": []}),
            }
        )
        _store_conllulex(sentence, token_list, errors, warnings, store_conllulex_string)

        for token in token_list:
            token_dict = {}
            is_ellipsis = isinstance(token["id"], Iterable) and len(token["id"]) == 3 and token["id"][1] == "."
            is_supertoken = isinstance(token["id"], Iterable) and len(token["id"]) == 3 and token["id"][1] == "-"
            if is_ellipsis or is_supertoken:
                token_dict["#"] = (
                    token["id"][0],
                    token["id"][2],
                    "".join([str(part) for part in token["id"]]),
                )
            else:
                token_dict["#"] = token["id"]
            token_dict.update(
                {
                    "word": token["form"],
                    "lemma": token["lemma"],
                    "upos": token["upos"],
                    "xpos": token["xpos"],
                }
            )

            if include_morph_deps:
                _store_morph_and_deps(token_dict, token, errors, warnings, is_ellipsis, is_supertoken, sent_id)

            if include_misc:
                token_dict["misc"] = serialize_field(token["misc"])

            for nullable_column in ("xpos", "feats", "edeps", "misc"):
                if token_dict[nullable_column] in ["_", None]:
                    token_dict[nullable_column] = None

            if not is_ellipsis and not is_supertoken:
                _store_conllulex_columns(sentence, token_dict, token, errors, warnings, ss_mapper)
                sentence["toks"].append(token_dict)
            elif is_ellipsis:
                sentence["etoks"].append(token_dict)

        sentences.append(sentence)

    return sentences, errors, warnings


def _write_json(sents, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(sents, indent=1))


def format_error(error):
    s = (
        f"{error['sentence_id']}:"
        f"  {error['explanation']}"
    )
    if error["token"] is not None:
        s += f"  Token: {pformat(dict(error['token']))}'"
    s += "\n"
    return s


def _write_errors(errors, warnings):
    print("Errors were found during validation:")

    print("=" * 80)
    print("= Errors")
    print("=" * 80)
    for i, error in enumerate(errors, start=1):
        print(f"- Error {i}.")
        print(format_error(error))

    if len(warnings) > 0:
        print("=" * 80)
        print("= Warnings")
        print("=" * 80)
    for warning in warnings:
        print(format_error(warning))

    print(f"Finished with {len(errors)} errors and {len(warnings)} warnings. No output has been written.")


def convert_conllulex_to_json(
    input_path,
    output_path,
    corpus,
    include_morph_deps=True,
    include_misc=True,
    validate_upos_lextag=True,
    validate_type=True,
    store_conllulex_string="none",
    override_mwe_render=False,
    ss_mapper=lambda x: x,
):
    """
    Read an input conllulex file, convert it into the JSON format, and write the result
    out to the output path. If there are validation errors, fail before writing anything
    and print errors out to stdout, like a compiler.

    Args:
        input_path: path to a conllulex file OR a json file
        output_path: path the output json file should be written to
        corpus: The corpus contained in the conllulex file. Needed for language-specific config.
        include_morph_deps: Whether to include CoNLL-U MORPH, HEAD, DEPREL, and EDEPS columns, if available,
            in the output json. FORM, UPOS, XPOS and LEMMA are always included.
        include_misc: Whether to include CoNLL-U MISC column, if available, in the output json.
        validate_upos_lextag: Whether to validate that UPOS and LEXTAG are compatible
        validate_type: Whether to validate SWE-specific or SMWE-specific tags that apply to the corresponding MWE type
        store_conllulex_string: Set to full to include all conllulex input lines as a string in the returned JSON,
            or set to toks to exclude ellipsis tokens and metadata lines
        override_mwe_render: When set, compare the given `# mwe = ...` metadata to an automatically generated version,
            print a warning, and use the automatically generated version in the output.
        ss_mapper: A function to apply to supersense labels to replace them in the returned data structure. Applies to
            all supersense labels (nouns, verbs, prepositions). Not applied if the supersense slot is empty.

    Returns:
        Nothing
    """
    sentences, errors, warnings = _load_sentences(
        input_path,
        include_morph_deps,
        include_misc,
        validate_upos_lextag,
        validate_type,
        store_conllulex_string,
        override_mwe_render,
        ss_mapper,
    )

    if len(errors) > 0:
        _write_errors(errors, warnings)
    else:
        _write_json(sentences, output_path)
