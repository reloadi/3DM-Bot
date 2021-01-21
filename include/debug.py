from datetime import datetime

DEBUG = True

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

# used for local debugging
def __debug(msg, text=False):
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


    if DEBUG:
        if not text:
            print("{0} {1} sent {2} in #{3}".format(dark(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), cyan(msg.author), invert(msg.content), red(msg.channel)), flush=True)
        else:
            print("{0} debug: {1}".format(dark(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), invert(msg)), flush=True)
