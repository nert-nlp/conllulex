"""
Rely on the standard conllu package to parse conllulex.
"""
import conllu


def get_conllulex_tokenlists(conllulex_path):
    """
    Parse a 19-column .conllulex file.

    Args:
        conllulex_path: a filepath to a conllulex file

    Returns: A list of `conllu.TokenList` for each sentence.
    `TokenList` is an iterable, and every token is a dictionary keyed by the name
    of its column, lowercased.

    """
    fields = tuple(
        list(conllu.parser.DEFAULT_FIELDS)
        + [
            "smwe",  # 10
            "lexcat",  # 11
            "lexlemma",  # 12
            "ss",  # 13
            "ss2",  # 14
            "wmwe",  # 15
            "wcat",  # 16
            "wlemma",  # 17
            "lextag",  # 18
        ]
    )

    with open(conllulex_path, "r", encoding="utf-8") as f:
        return conllu.parse(f.read(), fields=fields)
