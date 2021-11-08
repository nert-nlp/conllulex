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
            lambda d: (d["upos"] == "PRON"),  # and lexcat == "PRON" or lexcat == "PRON.POSS"
            lambda d: (d["lexcat"] == "ADV" and (d["upos"] == "ADV" or d["upos"] == "PART")),  # PART is for negations
            lambda d: (d["upos"] == "ADP" and d["lexcat"] == "CCONJ" and d["lemma"] == "versus"),
        ],
        "extra_prepositional_supersenses": set(),
        "mwe_lexlemma_mismatch_whitelist": {},
        "mwe_lexlemma_mismatch_xforms": [],
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
            ("PART", "P"),  # से
        },
        "mismatched_lexcat_exception_checks": [
            lambda d: (d["lexcat"] == "P" and d["upos"] == "PRON"),  # possessive pronouns
            lambda d: (d["lexcat"] == "ADV" and d["upos"] == "PART"),  # ही
        ],
        # TODO is this really needed
        "extra_prepositional_supersenses": {"p.Focus", "p.NONSNACS"},
        # It is assumed that lexlemma and lemma must match. Add exceptions here, where
        # the first item is the lemma and the second item is a list of forms which are
        # acceptable lexlemmas for that lemma.
        "mwe_lexlemma_mismatch_whitelist": {
            "का": ["के", "की"],
            "मैं": ["के", "की"],
            "हम": ["के", "की", "में", "से", "को"],
            "तू": ["के", "की", "में", "से", "को"],
            "तुम": ["के", "की", "में", "से", "को"],
            "आप": ["के", "की", "में", "से", "को"],
            "वह": ["के", "की", "में", "से", "को"],
            "यह": ["के", "की", "में", "से", "को"],
            "वे": ["के", "की", "में", "से", "को"],
            "ये": ["के", "की", "में", "से", "को"],
            "अपना": ["के", "की", "में", "से", "को"],
            "जो": ["के", "की", "में", "से", "को"],
            "सबसे": ["से"],
        },
        # Like above, but for lambdas applied to individual lemmas. All lambdas will be applied to both
        # the lexlemma computed from each token's lemma and the given lexlemma.
        "mwe_lexlemma_mismatch_xforms": [
            lambda lemma: lemma.replace("़", ""),
            lambda lemma: lemma.replace("ँ", "ं"),
            lambda lemma: lemma.replace("ख्य", "खय"),
        ],
    },
    "zh": {
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
            ("SCONJ", "P"),
            ("ADP", "DISC"),
            ("ADV", "DISC"),
            ("SCONJ", "DISC"),
            ("PART", "POSS"),
        },
        "mismatched_lexcat_exception_checks": [],
        "extra_prepositional_supersenses": set(),
        "mwe_lexlemma_mismatch_whitelist": {},
        "mwe_lexlemma_mismatch_xforms": [],
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
    },
}


def get_config(corpus_name):
    language_code = CORPUS_CFG[corpus_name]["language"]
    return LANG_CFG[language_code], CORPUS_CFG[corpus_name]
