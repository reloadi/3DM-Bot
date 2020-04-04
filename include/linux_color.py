"""
    just some short cut to make everything a little more cute.. -eric
"""

class _c:
    """return linux colored text of a string"""
    def blue(txt):
        return "\033[94m{0}\033[0m".format(txt)
    def dark(txt):
        return "\033[38;5;239m{0}\033[0m".format(txt)
    def cyan(txt):
        return "\033[38;5;14m{0}\033[0m".format(txt)
    def invert(txt):
        return "\033[48;5;239m{0}\033[0m".format(txt)
    def red(txt):
        return "\033[38;5;196m{0}\033[0m".format(txt)
