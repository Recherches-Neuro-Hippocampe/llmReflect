def message(msg, color=None):
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'blue': '\033[34m',
        'reset': '\033[0m',
        'yellow': '\033[33m'
    }

    if color not in COLORS.keys():
        color = 'reset'

    print(f'{COLORS[color]}{msg}{COLORS["reset"]}')
