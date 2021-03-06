"""
Contains language-specific information that is used across the package, e.g.
information about grammatically exceptional phrases or allowed/disallowed
role/function prepositional supersense combinations.
"""
LANG_CFG = {
    # English
    "en": {
        "permitted_ancestor_combos": {
            ("p.Circumstance", "p.Locus"),
            ("p.Circumstance", "p.Path"),
            ("p.Locus", "p.Goal"),
            ("p.Locus", "p.Source"),
            ("p.Characteristic", "p.Stuff"),
            ("p.Whole", "p.Gestalt"),
            ("p.Org", "p.Gestalt"),
            ("p.QuantityItem", "p.Gestalt"),
            ("p.Goal", "p.Locus"),
        },
        "banned_functions": {
            "p.Experiencer",
            "p.Stimulus",
            "p.Originator",
            "p.Recipient",
            "p.SocialRel",
            "p.Org",
            "p.OrgMember",
            "p.Ensemble",
            "p.QuantityValue",
        },
        "allowed_mismatched_upos_lexcat_pairs": {
            ("NOUN", "N"),
            ("PROPN", "N"),
            ("VERB", "V"),
            ("ADP", "P"),
            ("ADV", "P"),
            ("SCONJ", "P"),
            ("ADP", "DISC"),
            ("ADV", "DISC"),
            ("SCONJ", "DISC"),
            ("PART", "POSS"),
        },
        "mismatched_lexcat_exception_checks": [
            lambda d: d["xpos"] == "TO" and d["lexcat"].startswith("INF"),
            lambda d: (
                ((d["xpos"] == "TO") != d["lexcat"].startswith("INF"))
                and (d["upos"] == "SCONJ" and d["lexlemma"] == "for")
            ),
            lambda d: (
                ((d["upos"] in ("NOUN", "PROPN")) != (d["lexcat"] == "N"))
                and (d["upos"] in ("SYM", "X") or d["lexcat"] in ("PRON", "DISC"))
            ),
            lambda d: (
                ((d["upos"] == "AUX") != (d["lexcat"] == "AUX")) and (d["lemma"] == "be" and d["lexcat"] == "V")
            ),
            lambda d: (
                (d["upos"] == "VERB") != (d["lexcat"] == "V")
                and (d["lexcat"] == "ADJ" or (d["lemma"] == "be" and d["lexcat"] == "V"))
            ),
            lambda d: (d["upos"] == "PRON") and d["lexcat"] == "PRON" or d["lexcat"] == "PRON.POSS",
            lambda d: (d["lexcat"] == "ADV" and (d["upos"] == "ADV" or d["upos"] == "PART")),  # PART is for negations
            lambda d: (d["upos"] == "ADP" and d["lexcat"] == "CCONJ" and d["lemma"] == "versus"),
        ],
        "extra_prepositional_supersenses": set(),
        "mwe_lexlemma_mismatch_whitelist": {},
        "mwe_lexlemma_mismatch_xforms": [],
        "mwe_lexlemma_validation_column": "lemma",
        "lexcat_exception_list":{} # skip invalid supersense check for this list of lexcats
    },
    # Hindi
    "hi": {
        "permitted_ancestor_combos": {
            ("p.Circumstance", "p.Locus"),
            ("p.Circumstance", "p.Path"),
            ("p.Locus", "p.Goal"),
            ("p.Locus", "p.Source"),
            ("p.Characteristic", "p.Stuff"),
            ("p.Characteristic", "p.QuantityValue"),
            ("p.PartPortion", "p.Characteristic"),
            ("p.Gestalt", "p.Whole"),
            ("p.Whole", "p.Gestalt"),
            ("p.Org", "p.Gestalt"),
            ("p.QuantityItem", "p.Gestalt"),
            ("p.Goal", "p.Locus"),
            ("p.Topic", "p.Theme"),
        },
        "banned_functions": {
            "p.Experiencer",
            "p.Stimulus",
            "p.Originator",
            "p.SocialRel",
            "p.Org",
            "p.OrgMember",
            "p.Ensemble",
            # "p.QuantityValue",
        },
        "allowed_mismatched_upos_lexcat_pairs": {
            # from English
            ("NOUN", "N"),
            ("PROPN", "N"),
            ("VERB", "V"),
            ("ADP", "P"),
            ("ADV", "P"),
            ("SCONJ", "P"),
            ("ADP", "DISC"),
            ("ADV", "DISC"),
            ("SCONJ", "DISC"),
            ("PART", "POSS"),
            # for Hindi
            ("PART", "P"),  # ??????
        },
        "mismatched_lexcat_exception_checks": [
            lambda d: (d["lexcat"] == "P" and d["upos"] == "PRON"),  # possessive pronouns
            lambda d: (d["lexcat"] == "ADV" and d["upos"] == "PART"),  # ??????
        ],
        # TODO is this really needed? These probably ought to just live in supersenses.py
        "extra_prepositional_supersenses": {"p.Focus", "p.NONSNACS"},
        # It is assumed that lexlemma and lemma must match. Add exceptions here, where
        # the first item is the lemma and the second item is a list of forms which are
        # acceptable lexlemmas for that lemma.
        "mwe_lexlemma_mismatch_whitelist": {
            "??????": ["??????", "??????"],
            "?????????": ["??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "?????????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "????????????": ["??????", "??????", "?????????", "??????", "??????"],
            "??????": ["??????", "??????", "?????????", "??????", "??????"],
            "????????????": ["??????"],
        },
        # Like above, but for lambdas applied to individual lemmas. All lambdas will be applied to both
        # the lexlemma computed from each token's lemma and the given lexlemma.

        # undoing and commenting out.

        "mwe_lexlemma_mismatch_xforms": [
        #    lambda lemma: lemma.replace("???", ""),
        #    lambda lemma: lemma.replace("???", "???"),
        #    lambda lemma: lemma.replace("?????????", "??????"),
        ],
        "mwe_lexlemma_validation_column": "word",
        "lexcat_exception_list":{'PRON','PART'}, # skip invalid supersense check for this list of lexcats
    },
    "zh": {
        "permitted_ancestor_combos": {
            ("p.Circumstance", "p.Time"),
            ("p.Circumstance", "p.Locus"),
            ("p.Circumstance", "p.Path"),
            ("p.Locus", "p.Goal"),
            ("p.Locus", "p.Source"),
            ("p.Characteristic", "p.Stuff"),
            ("p.Whole", "p.Gestalt"),
            ("p.Org", "p.Gestalt"),
            ("p.QuantityItem", "p.Gestalt"),
            ("p.Goal", "p.Locus"),
            ("p.Circumstance", "p.Time"),
        },
        "banned_functions": {
            "p.Stimulus",
            "p.Originator",
            "p.SocialRel",
            "p.Org",
            "p.OrgMember",
            "p.QuantityValue",
        },
        "allowed_mismatched_upos_lexcat_pairs": {
            # from English
            ("NOUN", "N"),
            ("PROPN", "N"),
            ("VERB", "V"),
            ("ADP", "P"),
            ("ADV", "P"),
            ("PART", "ADV"),
            ("VERB", "P"),
            ("SCONJ", "P"),
            ("ADP", "DISC"),
            ("ADV", "DISC"),
            ("SCONJ", "DISC"),
            ("PART", "POSS"),
        },
        "mismatched_lexcat_exception_checks": [
            lambda d: d["xpos"] in  ["LC", "BA", "LB"], # Localizers, BA ??? and BEI ???
            lambda d: (d["lexcat"] == "DISC" and d["upos"] == "P"),
            lambda d: d["lexlemma"] in  ["??????",  "??????", "?????????", "???", "???"],
            lambda d: (d["lexcat"] == "P" and d["upos"] == "VV"
                       and d["lexlemma"] in ["???", "???", "???", "???", "???", "???", "???", "???"]),
        ],
        "extra_prepositional_supersenses": set(),
        "mwe_lexlemma_mismatch_whitelist": {},
        "mwe_lexlemma_mismatch_xforms": [],
        "mwe_lexlemma_validation_column": "lemma",
        "lexcat_exception_list":{}, # skip invalid supersense check for this list of lexcats
    },
}

CORPUS_CFG = {
    "streusle": {
        "language": "en",
        "enrichment_subtasks": [],
        "supersense_annotated": ["N", "V", "P"],
        "require_sentence_numbers_from_1": True,
        "require_sentence_numbers_consecutive": True,
    },
    "pastrie": {
        "language": "en",
        "enrichment_subtasks": [
            "dedupe_question_marks",
            "make_compound_prts_smwes",
            "add_mwe_metadatum",
            "add_lexlemma",
            "add_wlemma",
            "prefix_prepositional_supersenses",
            "add_lexcat",
            "add_lextag",
            "renumber_mwes",
        ],
        "supersense_annotated": ["P"],
        "require_sentence_numbers_from_1": True,
        "require_sentence_numbers_consecutive": True,
    },
    "prince_en": {
        "language": "en",
        "enrichment_subtasks": [
            ["run_through_pipeline", "en"],
            "add_mwe_metadatum",
            "add_lexlemma",
            "add_wlemma",
            "add_lexcat",
            "add_lextag",
            "renumber_mwes",
        ],
        "supersense_annotated": ["P"],
        "doc_id_fn": lambda x: x.rsplit(".", 1)[0],
        "sent_num_fn": lambda x: x.rsplit(".", 1)[1],
        "require_sentence_numbers_from_1": False,
        "require_sentence_numbers_consecutive": False,
    },
    "prince_zh": {
        "language": "zh",
        "enrichment_subtasks": [
            "capitalize_supersenses",
            "assign_sent_id",
            "add_mwe_metadatum",
            "add_lexlemma",
            "add_wlemma",
            "add_lexcat",
            "add_lextag",
            "renumber_mwes",
        ],
        "supersense_annotated": ["P"],
        "require_sentence_numbers_from_1": True,
        "require_sentence_numbers_consecutive": True,
    },
    "prince_hi": {
        "language": "hi",
        "enrichment_subtasks": [
            "dedupe_question_marks",
            "add_mwe_metadatum",
            "add_lexlemma",
            "add_wlemma",
            "add_lexcat",
            "add_lextag",
            "renumber_mwes",
        ],
        "supersense_annotated": ["P"],
        "require_sentence_numbers_from_1": True,
        "require_sentence_numbers_consecutive": True,
    },
}


def get_config(corpus_name):
    language_code = CORPUS_CFG[corpus_name]["language"]
    return LANG_CFG[language_code], CORPUS_CFG[corpus_name]
