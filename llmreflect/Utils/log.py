import logging
import os

tmp_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(tmp_log_dir):
    os.mkdir(tmp_log_dir)

LOGGER = logging.getLogger('llmreflect')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(
    logging.FileHandler(
        filename=os.path.join(tmp_log_dir, 'llmreflect.log'), mode='a+',))


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


def openai_cb_2_str(cb) -> str:
    tmp_str = ""
    tmp_str += f"Total Tokens: {cb.total_tokens} \n"
    tmp_str += f"Prompt Tokens: {cb.prompt_tokens} \n"
    tmp_str += f"Completion Tokens: {cb.completion_tokens} \n"
    tmp_str += f"Successful Requests: {cb.successful_requests} \n"
    tmp_str += f"Total Cost (USD): ${cb.total_cost} \n"
    return tmp_str
