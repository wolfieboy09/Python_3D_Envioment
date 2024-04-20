import sys

# Define color escape codes
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m'
}


def debug(msg):
    sys.stdout.write(f"{COLORS['CYAN']}[DEBUG] {msg}{COLORS['RESET']}\n")


def info(msg):
    sys.stdout.write(f"{COLORS['GREEN']}[INFO] {msg}{COLORS['RESET']}\n")


def warning(msg):
    sys.stdout.write(f"{COLORS['YELLOW']}[WARNING] {msg}{COLORS['RESET']}\n")


def error(msg):
    sys.stderr.write(f"{COLORS['RED']}[ERROR] {msg}{COLORS['RESET']}\n")


def critical(msg):
    sys.stderr.write(f"{COLORS['RED']}[CRITICAL] {msg}{COLORS['RESET']}\n")
