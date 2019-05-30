class Color:
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    ENDC = '\033[0m'

    @staticmethod
    def black(string):
        return Color.colored_format(string, Color.BLACK)

    @staticmethod
    def red(string):
        return Color.colored_format(string, Color.RED)

    @staticmethod
    def green(string):
        return Color.colored_format(string, Color.GREEN)

    @staticmethod
    def blue(string):
        return Color.colored_format(string, Color.BLUE)

    @staticmethod
    def yellow(string):
        return Color.colored_format(string, Color.YELLOW)

    @staticmethod
    def colored_format(string, color):
        return color + string + Color.ENDC
