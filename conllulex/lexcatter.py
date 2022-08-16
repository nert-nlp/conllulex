from copy import deepcopy

from conllulex.supersenses import NSS, PSS, VSS


def supersenses_for_lexcat(lc, language=None):

    if lc == "N":
        return NSS
    if lc == "V" or lc.startswith("V."):
        if lc != "V":
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
    if lc == "PRON" and language == "hi":  # for Hindi
        return PSS | {"p.Focus", "p.`d"}


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

HI_LEXCATS = deepcopy(BASE_LEXCATS)
HI_LEXCATS.add("PART")
HI_LEXCATS.add("PRON.NOM")
HI_LEXCATS.add("PRON.OBL")  # 'koi','usi', etc
HI_LEXCATS.add("PRON.WH")  # wh-pronouns 'kahaan','kaise', etc
HI_LEXCATS.add("PRON.REFL")  # reflexive pronoun 'apna', 'ap'
HI_LEXCATS.add("PART.FOC")

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


def get_lexcat_set(language_code):
    if language_code == "zh":
        return ZH_LEXCATS
    if language_code == "hi":
        return HI_LEXCATS
    return BASE_LEXCATS
