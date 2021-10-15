"""
Contains language-specific information that is used across the package, e.g.
information about grammatically exceptional phrases or allowed/disallowed
role/function prepositional supersense combinations.
"""
LANG_CFG = {
    # English
    "en": {},
    # Hindi
    "hi": {},
}

CORPUS_CFG = {
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
    },
}


def get_config(corpus_name):
    language_code = CORPUS_CFG[corpus_name]["language"]
    return LANG_CFG[language_code], CORPUS_CFG[corpus_name]
