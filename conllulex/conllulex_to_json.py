import json
import re
import sys
from collections import defaultdict
from functools import partial
from itertools import chain
from pprint import pprint, pformat
from typing import Iterable

from conllu.serializer import serialize_field

from conllulex.config import get_config
from conllulex.mwe_render import render
from conllulex.reading import get_conllulex_tokenlists
from conllulex.supersenses import ancestors, makesslabel
from conllulex.lexcatter import supersenses_for_lexcat, ALL_LEXCATS
from conllulex.tagging import sent_tags


def _append_if_error(errors, sentence_id, test, explanation, token=None):
    """
    If a test fails, append an error/warning dictionary to errors.

    Args:
        errors: a list of errors
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

    return modified_sentences, errors


def _store_conllulex(sentence, token_list, errors, store_conllulex_string):
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


def _store_metadata(sentence, token_list, errors):
    banned_keys = ["toks", "swes", "smwes", "wmwes"]
    metadata = token_list.metadata
    _append_if_error(
        errors,
        sentence["sent_id"],
        all(k not in metadata for k in banned_keys),
        '"toks", "swes", "smwes", and "wmwes" are not allowed to be metadata keys',
    )
    for k, v in metadata.items():
        if k not in banned_keys and not any(skip in k for skip in ["TODO"]):
            sentence[k] = v


def _store_morph_and_deps(token_dict, token, errors, is_ellipsis, is_supertoken, sent_id):
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
            token=token,
        )
        token_dict["head"] = None
    if token["deprel"] == "_":
        _append_if_error(
            errors,
            sent_id,
            is_ellipsis or is_supertoken,
            f"Only ellipsis tokens and supertokens are allowed to not have a deprel",
            token=token,
        )
        token_dict["deprel"] = None


def _store_conllulex_columns(sentence, token_dict, token, errors, ss_mapper):
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
            token=token,
        )
        if smwe_position == 1:
            _append_if_error(
                errors,
                sent_id,
                " " in token["lexlemma"],
                f"Token is the beginning of a SMWE, but lexlemma doesn't appear to have multiple tokens in it. ",
                token=token,
            )
            sentence["smwes"][smwe_group]["lexlemma"] = token["lexlemma"]
            _append_if_error(errors, sent_id, token["lexcat"] != "_", f"SMWE token lacks a lexcat. ", token=token)
            sentence["smwes"][smwe_group]["lexcat"] = token["lexcat"]
            sentence["smwes"][smwe_group]["ss"] = ss_mapper(token["ss"]) if token["ss"] != "_" else None
            sentence["smwes"][smwe_group]["ss2"] = ss_mapper(token["ss2"]) if token["ss2"] != "_" else None
        else:
            _append_if_error(
                errors,
                sent_id,
                token["lexlemma"] == "_",
                f"Non-initial tokens in SMWEs should always have lexlemma '_'.",
                token=token,
            )
            _append_if_error(
                errors,
                sent_id,
                token["lexcat"] == "_",
                f"Non-initial tokens in SMWEs should always have lexcat '_'.",
                token=token,
            )
    else:
        token_dict["smwe"] = None
        _append_if_error(
            errors,
            sent_id,
            token["lexlemma"] == token["lemma"],
            f"Single-word expression lemma \"{token['lexlemma']}\" doesn't match token lemma \"{token['lemma']}\"",
            token=token,
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
            token=token,
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
                token=token,
            )
            _append_if_error(
                errors,
                sent_id,
                token["wcat"] == "_",
                f"Non-initial tokens in SMWEs should always have wcat '_'.",
                token=token,
            )
    else:
        token_dict["wmwe"] = None
        _append_if_error(
            errors,
            sent_id,
            token["wlemma"] == "_",
            f"wlemma should be _ if token does not belong to WMWE, but token has wlemma value: {token['wlemma']}",
            token=token,
        )
        _append_if_error(
            errors,
            sent_id,
            token["wcat"] == "_",
            f"wcat should be _ if token does not belong to WMWE, but token has wcat value: {token['wcat']}",
            token=token,
        )

    lextag = token["lextag"]
    for m in re.finditer(r"\b[a-z]\.[A-Za-z/-]+", token["lextag"]):
        lextag = lextag.replace(m.group(0), ss_mapper(m.group(0)))
    for m in re.finditer(r"\b([a-z]\.[A-Za-z/-]+)\|\1\b", lextag):
        # e.g. p.Locus|p.Locus due to abstraction of p.Goal|p.Locus
        lextag = lextag.replace(m.group(0), m.group(1))  # simplify to p.Locus
    token_dict["lextag"] = lextag


def _validate_sentence_ids(sentences, errors):
    """
    Sentences are requried to have `sent_id` equal to something like `...-01` where the last bit, conforming
    to regex /-\\d+/, indicates the number of the sentence within the document.
    """
    sent_ids = [s.metadata["sent_id"] for s in sentences]
    doc_id = lambda x: x.rsplit('-', 1)[0]
    sent_num = lambda x: int(x.rsplit('-', 1)[1])
    _append_if_error(
        errors,
        sent_ids[0],
        len(set(sent_ids)) == len(sent_ids),
        "Sentence IDs must be unique",
        {"sent_ids": sent_ids}
    )

    sent_ids_by_doc = defaultdict(list)
    for sent_id in sent_ids:
        sent_ids_by_doc[doc_id(sent_id)].append(sent_id)
    for doc_id, doc_sent_ids in sent_ids_by_doc.items():
        try:
            doc_sent_numbers = [sent_num(sid) for sid in doc_sent_ids]
        except ValueError:
            _append_if_error(errors, sent_ids[0], False,
                             "All sentence ids must match the regex /.*-\\d+/ (e.g. `-001`)")
            return
        _append_if_error(
            errors,
            doc_id,
            doc_sent_numbers[0] == 1,
            "Sentence IDs must begin at 1",
            {"doc_sent_ids": doc_sent_ids}
        )
        _append_if_error(
            errors,
            doc_id,
            doc_sent_numbers == list(range(1, len(doc_sent_numbers) + 1)),
            "Sentence IDs must be monotonically increasing",
            {"doc_sent_ids": doc_sent_ids}
        )


def _load_sentences(
    input_path,
    include_morph_deps,
    include_misc,
    store_conllulex_string,
    ss_mapper,
):
    errors = []
    sentences = []
    if input_path.endswith(".json"):
        return _load_json(input_path, ss_mapper, include_morph_deps, include_misc)

    token_lists = get_conllulex_tokenlists(input_path)
    _validate_sentence_ids(token_lists, errors)

    for token_list in token_lists:
        sent_id = token_list.metadata["sent_id"]
        sentence = {
            "sent_id": sent_id,
        }
        _store_metadata(sentence, token_list, errors)
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
        _store_conllulex(sentence, token_list, errors, store_conllulex_string)

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
                _store_morph_and_deps(token_dict, token, errors, is_ellipsis, is_supertoken, sent_id)

            if include_misc:
                token_dict["misc"] = serialize_field(token["misc"])

            for nullable_column in ("xpos", "feats", "edeps", "misc"):
                if token_dict[nullable_column] in ["_", None]:
                    token_dict[nullable_column] = None

            if not is_ellipsis and not is_supertoken:
                _store_conllulex_columns(sentence, token_dict, token, errors, ss_mapper)
                sentence["toks"].append(token_dict)
            elif is_ellipsis:
                sentence["etoks"].append(token_dict)

        sentences.append(sentence)

    return sentences, errors


def _write_json(sents, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(sents, indent=1))


def format_error(error):
    s = f"{error['sentence_id']}:" f" {error['explanation']}"
    if error["token"] is not None:
        s += f"\n  Token: {pformat(dict(error['token']))}'"
    s += "\n"
    return s


def _write_errors(errors):
    print("Errors were found during validation:")

    errors = sorted(errors, key=lambda e: (e["explanation"], e["sentence_id"]))
    for i, error in enumerate(errors, start=1):
        print(f"- Error {i}.")
        print(format_error(error))

    print(f"Found a total of {len(errors)} errors.")


def _mwe_lexlemma_valid(lang_config, sentence, smwe):
    xforms = lang_config["mwe_lexlemma_mismatch_xforms"]

    def apply_xforms(xforms, value):
        for xform in xforms:
            value = xform(value)
        return value

    possible_lexlemmas = {" ".join(apply_xforms(xforms, sentence["toks"][i - 1]["lemma"]) for i in smwe["toknums"])}

    for lemma, mismatched_lexlemmas in lang_config["mwe_lexlemma_mismatch_whitelist"].items():
        for mismatched_lexlemma in mismatched_lexlemmas:
            possible_lexlemmas.add(
                " ".join(
                    apply_xforms(
                        xforms,
                        mismatched_lexlemma
                        if sentence["toks"][i - 1]["lemma"] == lemma
                        else sentence["toks"][i - 1]["lemma"],
                    )
                    for i in smwe["toknums"]
                )
            )

    xformed_lexlemma = " ".join(apply_xforms(xforms, x) for x in smwe["lexlemma"].split(" "))
    return xformed_lexlemma in possible_lexlemmas, possible_lexlemmas, xformed_lexlemma


def _validate_sentences(corpus, sentences, errors, validate_upos_lextag, validate_type, override_mwe_render):
    lexcat_tbd_count = 0

    lang_config, corpus_config = get_config(corpus)

    for sentence in sentences:
        sent_id = sentence["sent_id"]
        assert_ = partial(_append_if_error, errors, sent_id)
        for i, tok in enumerate(sentence["toks"], 1):
            assert_(tok["#"], "Tokens should be numbered from 1, in order")

        # check that MWEs are numbered from 1 based on first token offset
        xmwes = [(e["toknums"][0], "s", mwe_num) for mwe_num, e in sentence["smwes"].items()]
        xmwes += [(e["toknums"][0], "w", mwe_num) for mwe_num, e in sentence["wmwes"].items()]
        xmwes.sort()
        for k, mwe in chain(sentence["smwes"].items(), sentence["wmwes"].items()):
            assert_(int(k) - 1 < len(xmwes), f"MWE index {k} exceeds number of MWEs in the sentence")
            assert_(xmwes[int(k) - 1][2] == k, f"MWEs are not numbered in the correct order")

        # check that lexical & weak MWE lemmas are correct
        lex_exprs_to_validate = chain(sentence["swes"].values(), sentence["smwes"].values()) if validate_type else []
        for lex_expr in lex_exprs_to_validate:
            assert_(
                lex_expr["lexlemma"] == " ".join(sentence["toks"][i - 1]["lemma"] for i in lex_expr["toknums"]),
                f"MWE lemma is incorrect: {lex_expr} vs. {sentence['toks'][lex_expr['toknums'][0] - 1]}",
                token=lex_expr,
            )
            lexcat = lex_expr["lexcat"]
            if lexcat.endswith("!@"):
                lexcat_tbd_count += 1

            if lexcat.startswith("V") and "V" not in corpus_config["supersense_annotated"]:
                valid_ss = set()
            elif lexcat == "N" and "N" not in corpus_config["supersense_annotated"]:
                valid_ss = set()
            elif lexcat in ["P", "PP"] and "P" not in corpus_config["supersense_annotated"]:
                valid_ss = set()
            else:
                valid_ss = supersenses_for_lexcat(lexcat)
                if lexcat in ["P", "PP"] and "P" in corpus_config["supersense_annotated"]:
                    valid_ss = valid_ss | lang_config["extra_prepositional_supersenses"]
            if "V" in corpus_config["supersense_annotated"] and lexcat == "V":
                assert_(
                    len(lex_expr["toknums"]) == 1,
                    f'Verbal MWE "{lex_expr["lexlemma"]}" lexcat must be subtyped (V.VID, etc., not V)',
                    token=lex_expr,
                )
            ss, ss2 = lex_expr["ss"], lex_expr["ss2"]
            if valid_ss:
                if ss == "??":
                    assert_(ss2 is None, "When using the '??' supersense annotation in ss, ss2 should be blank")
                elif ss is None:
                    assert_(False, f"Missing supersense annotation in lexical entry: {lex_expr}", token=lex_expr)
                elif ss not in valid_ss:
                    assert_(False, f"Invalid supersense(s) in lexical entry: {lex_expr}", token=lex_expr)
                elif (lexcat in ("N", "V") or lexcat.startswith("V.")) and ss2 is not None:
                    assert_(False, f"Noun/verb should not have ss2 annotation: {lex_expr}", token=lex_expr)
                elif ss2 is not None and ss2 not in valid_ss:
                    assert_(False, f"Invalid ss2: {lex_expr}", token=lex_expr)
                elif ss is not None and ss.startswith("p."):
                    assert_(
                        ss2.startswith("p."),
                        "Found an ss2 not prefixed with p. when ss was prefixed with p.",
                        token=lex_expr,
                    )
                    if ss != ss2:
                        assert_(
                            ss2 not in lang_config["banned_functions"],
                            f"{ss2} should never be function",
                            token=lex_expr,
                        )
                        ss_ancestors, ss2_ancestors = ancestors(ss), ancestors(ss2)
                        # there are just a few permissible combinations where one is the ancestor of the other
                        if (ss, ss2) not in lang_config["permitted_ancestor_combos"]:
                            assert_(ss not in ss2_ancestors, f"unexpected construal: {ss} ~> {ss2}", token=lex_expr)
                            assert_(ss2 not in ss_ancestors, f"unexpected construal: {ss} ~> {ss2}", token=lex_expr)
            else:
                assert_(
                    ss is None and ss2 is None and lexcat not in ("P", "INF.P", "PP", "POSS", "PRON.POSS"),
                    f"Invalid supersense(s) in lexical entry",
                    token=lex_expr,
                )

        # check lexcat on single-word expressions
        for swe in sentence["swes"].values():
            tok = sentence["toks"][swe["toknums"][0] - 1]
            upos, xpos = tok["upos"], tok["xpos"]
            lexcat = swe["lexcat"]
            if lexcat.endswith("!@"):
                continue
            if lexcat not in ALL_LEXCATS:
                assert_(not validate_type, f"invalid lexcat {lexcat} for single-word expression '{tok['word']}'")
                continue
            if (
                validate_upos_lextag
                and upos != lexcat
                and (upos, lexcat) not in lang_config["allowed_mismatched_upos_lexcat_pairs"]
            ):
                mismatchOK = False
                for f in lang_config["mismatched_lexcat_exception_checks"]:
                    mismatchOK = mismatchOK or f(
                        {
                            "xpos": xpos,
                            "upos": upos,
                            "lemma": tok["lemma"],
                            "lexlemma": swe["lexlemma"],
                            "lexcat": lexcat,
                        }
                    )

                assert_(
                    mismatchOK,
                    f"single-word expression '{tok['word']}' has lexcat {lexcat}, "
                    f"which is incompatible with its upos {upos}",
                )
            if validate_type:
                assert_(
                    lexcat != "PP",
                    f"PP should only apply to strong MWEs, but occurs for a single-word expression",
                    token=tok,
                )
        for smwe in sentence["smwes"].values():
            assert_(len(smwe["toknums"]) > 1, "SMWEs must have more than one token", token=smwe)
            correct, possible_lexlemmas, xformed_lexlemma = _mwe_lexlemma_valid(lang_config, sentence, smwe)
            assert_(
                correct,
                "lexlemma appears incorrect for smwe",
                token={**smwe, "possible_lexlemmas": possible_lexlemmas, "transformed_lexlemma": xformed_lexlemma},
            )
        for wmwe in sentence["wmwes"].values():
            assert_(len(wmwe["toknums"]) > 1, "WMWEs must have more than one token", token=wmwe)
            correct, possible_lexlemmas, xformed_lexlemma = _mwe_lexlemma_valid(lang_config, sentence, wmwe)
            assert_(
                correct,
                "lexlemma appears incorrect for smwe",
                token={**wmwe, "possible_lexlemmas": possible_lexlemmas, "transformed_lexlemma": xformed_lexlemma},
            )
        # we already checked that noninitial tokens in an MWE have _ as their lemma

        # check lextags
        smwe_groups = [smwe["toknums"] for smwe in sentence["smwes"].values()]
        wmwe_groups = [wmwe["toknums"] for wmwe in sentence["wmwes"].values()]
        tagging = sent_tags(len(sentence["toks"]), sentence["mwe"], smwe_groups, wmwe_groups)
        for tok, tag in zip(sentence["toks"], tagging):
            full_lextag = tag
            if tok["smwe"]:
                smwe_number, position = tok["smwe"]
                lex_expr = sentence["smwes"][smwe_number]
            else:
                position = None
                lex_expr = sentence["swes"][tok["#"]]

            if position is None or position == 1:
                lexcat = lex_expr["lexcat"]
                full_lextag += "-" + lexcat
                ss_label = makesslabel(lex_expr)
                if ss_label:
                    full_lextag += "-" + ss_label

                if tok["wmwe"]:
                    wmwe_number, position = tok["wmwe"]
                    wmwe = sentence["wmwes"][wmwe_number]
                    wcat = wmwe["lexcat"]
                    if wcat and position == 1:
                        full_lextag += "+" + wcat

            assert_(
                tok["lextag"] == full_lextag,
                f"the full tag at the end of the line is inconsistent with the rest of the line ({full_lextag} expected)",
                token=tok,
            )

        # check rendered MWE string
        s = render([tok["word"] for tok in sentence["toks"]], smwe_groups, wmwe_groups)
        if sentence["mwe"] != s:
            caveat = " (may be due to simplification)" if "$1" in sentence["mwe"] else ""
            if override_mwe_render:
                caveat += " (OVERRIDING)"
                sentence["mwe"] = s
            else:
                print(f"MWE string mismatch{caveat}: {s}, {sentence['mwe']}, {sentence['sent_id']}", file=sys.stderr)


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
    force_write=False,
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
        override_mwe_render: When not set to true, compare the given `# mwe = ...` metadata to an automatically
            generated version and report an error if there is a mismatch. Otherwise, silently override.
        ss_mapper: A function to apply to supersense labels to replace them in the returned data structure. Applies to
            all supersense labels (nouns, verbs, prepositions). Not applied if the supersense slot is empty.
        force_write: when True, produce output regardless of errors

    Returns:
        Nothing
    """
    sentences, errors = _load_sentences(
        input_path,
        include_morph_deps,
        include_misc,
        store_conllulex_string,
        ss_mapper,
    )

    _validate_sentences(corpus, sentences, errors, validate_upos_lextag, validate_type, override_mwe_render)

    if len(errors) == 0:
        _write_json(sentences, output_path)
    else:
        if force_write:
            _write_errors(errors)
            print("`ignore_validation_errors` was set to true, writing output anyway")
            _write_json(sentences, output_path)
            print(f"Wrote {len(sentences)} sentences to {output_path}")
        else:
            _write_errors(errors)
            print("Errors were found. No output was written.")
