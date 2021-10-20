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
            lambda xpos, upos, lemma, lexlemma, lexcat: (xpos == "TO" and lexcat.startswith("INF")),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                ((xpos == "TO") != lexcat.startswith("INF")) and (upos == "SCONJ" and lexlemma == "for"),
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                (upos in ("NOUN", "PROPN") != (lexcat == "N")) and (upos in ("SYM", "X") or lexcat in ("PRON", "DISC"))
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                ((upos == "AUX") != (lexcat == "AUX")) and (lemma == "be" and lexcat == "V")
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                ((upos == "VERB") != (lexcat == "V") and (lexcat == "ADJ" or (lemma == "be" and lexcat == "V")))
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                upos == "PRON"  # and lexcat == "PRON" or lexcat == "PRON.POSS"
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (
                lexcat == "ADV" and (upos == "ADV" or upos == "PART")  # PART is for negations
            ),
            lambda xpos, upos, lemma, lexlemma, lexcat: (upos == "ADP" and lexcat == "CCONJ" and lemma == "versus"),
        ],
        "extra_prepositional_supersenses": set(),
        "mwe_lexlemma_mismatch_whitelist": {},
    },
    # Hindi
    "hi": {
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
            "p.SocialRel",
            "p.Org",
            "p.OrgMember",
            "p.Ensemble",
            "p.QuantityValue",
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
            ("PART", "P"),  # से
        },
        "mismatched_lexcat_exception_checks": [
            lambda xpos, upos, lemma, lexlemma, lexcat: (lexcat == "P" and upos == "PRON"),  # possessive pronouns
            lambda xpos, upos, lemma, lexlemma, lexcat: (lexcat == "ADV" and upos == "PART"),  # ही
        ],
        # TODO is this really needed
        "extra_prepositional_supersenses": {"p.Focus", "p.NONSNACS"},
        # It is assumed that lexlemma and lemma must match. Add exceptions here, where
        # the first item is the lemma and the second item is a list of forms which are
        # acceptable lexlemmas for that lemma.
        "mwe_lexlemma_mismatch_whitelist": {"का": ["के", "की"]},
    },
}

CORPUS_CFG = {
    "streusle": {"language": "en", "enrichment_subtasks": [], "supersense_annotated": ["N", "V", "P"]},
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
    },
    "hindi": {
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
    },
}


def get_config(corpus_name):
    language_code = CORPUS_CFG[corpus_name]["language"]
    return LANG_CFG[language_code], CORPUS_CFG[corpus_name]
