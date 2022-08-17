from conllulex.supersenses import NSS, PSS, VSS


def supersenses_for_lexcat(lc, language=None):
    if language == "la":
        if lc in ["P", "N.P", "PRON.P", "SUBST", "V.GER"]:
            return PSS
        return set()

    if lc == "N":
        return NSS

    if lc == "V" or lc.startswith("V."):
        if lc != "V":
            if language == "en":
                assert lc in {
                    "V.VID",
                    "V.VPC.full",
                    "V.VPC.semi",
                    "V.LVC.full",
                    "V.LVC.cause",
                    "V.IAV",
                }, lc  # PARSEME 1.1 verbal MWE subtypes
        return VSS
    if lc in ("P", "PP", "INF.P", "PART.FOC"):
        return PSS | {"p.Focus", "p.`d", "p.`i"}
    if lc in ("POSS", "PRON.POSS"):
        return PSS | {"`$"}
    if lc == "PRON":  # for Hindi
        if language == "hi":
            return PSS | {"p.Focus", "p.`d"}
    return set()


BASE_LEXCATS = {
    "N",
    "PRON",
    "V",
    "P",
    "PP",
    "INF",
    "INF.P",
    "POSS",
    "PRON.POSS",
    "DISC",
    "AUX",
    "ADJ",
    "ADV",
    "DET",
    "CCONJ",
    "SCONJ",
    "INTJ",
    "NUM",
    "SYM",
    "PUNCT",
    "X",
}

HI_LEXCATS = BASE_LEXCATS | {
    "PART",
    "PRON.NOM",
    "PRON.OBL",  # 'koi','usi', etc
    "PRON.WH",  # wh-pronouns 'kahaan','kaise', etc
    "PRON.REFL",  # reflexive pronoun 'apna', 'ap'
    "PART.FOC",
}

ZH_LEXCATS = {
    "BA",  # 把
    "DE",  # DER, DEC, DEG, DEV
    "LB",  # long bei 被
    "LC",  # localizer
    "MSP",  # suo 所 lai 来
    "N",
    "PRON",
    "V",
    "P",
    "AUX",
    "ADJ",
    "ADV",
    "DET",
    "PART",
    "CCONJ",
    "SCONJ",
    "INTJ",
    "NUM",
    "SYM",
    "PUNCT",
    "DISC",
    "X",
}

LA_LEXCATS = {
    # From base
    "N",
    "PRON",
    "V",
    "P",
    "DISC",
    "AUX",
    "ADJ",
    "ADV",
    "DET",
    "CCONJ",
    "SCONJ",
    "INTJ",
    "NUM",
    "SYM",
    "PUNCT",
    "X",

    # New for Latin
    "V.GER",  # Gerunds, e.g. eundo. Substantive gerundives like "clamantis" in "vox in deserto clamantis" are SUBST
    "SUBST",  # This covers participles, adjectives, and determiners that lack a noun head
    "V.SUBJINF",  # infinitive when in subject position
    # Noun that is an annotation target
    "N.P",
    # pronoun when it is standalone--this excludes cases when its marking is agreeing with a syntactic head,
    # like "qui homines", and when it is the obj of a preposition
    "PRON.P",
}

_language_map = {
    "zh": ZH_LEXCATS,
    "hi": HI_LEXCATS,
    "la": LA_LEXCATS,
}


def get_lexcat_set(language_code):
    return _language_map.get(language_code, BASE_LEXCATS)
