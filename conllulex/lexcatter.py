from conllulex.supersenses import NSS, VSS, PSS


def supersenses_for_lexcat(lc,language_code = None):

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
    if lc in ("P", "PP", "INF.P"):
        PSS.add('p.Focus')  # to revisit - version 2.7
        PSS.add('p.`d')  # to revisit - version 2.7
        PSS.add('p.`i')  # to revisit - version 2.7
        return PSS
    if lc in ("POSS", "PRON.POSS"):
        return PSS | {"`$"}

    # irregular pronouns in hindi marked for oblique case and with an inflection in place of the post-position (See Yamuna Kachru's Hindi grammar book, section on pronouns).
    # it's not clear always that a post-position should be extracted from the morphology; i couldn't find any theory for irregular genitive pronouns, though there is some backing for extracting accusative/dative postpositions into a separate token out of the irregular pronoun
    # And so, all irregular pronouns marked with oblique case and inflected get the prepositional SNACS label. Any feedback appreciated :)
    if language_code == 'hi' and lc == 'PRON':
        return PSS

    # PARTicles have been annotated with preposition supersenses. Particles UPOS was determined by UD parsing. May need to revisit in v2.7
    if language_code == 'hi' and lc == 'PART':
        PSS.add('p.Focus') #to revisit - version 2.7
        PSS.add('p.`d')  # to revisit - version 2.7
        PSS.add('p.`i')  # to revisit - version 2.7
        return PSS





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

HI_LEXCATS = BASE_LEXCATS
HI_LEXCATS.add('PART')
HI_LEXCATS.add('`d')
HI_LEXCATS.add('`i')

ZH_LEXCATS = {
    "BA", # 把
    "DE", # DER, DEC, DEG, DEV
    "LB", # long bei 被
    "LC", # localizer
    "MSP", # suo 所 lai 来
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
    if language_code == 'hi':
        return HI_LEXCATS
    return BASE_LEXCATS
