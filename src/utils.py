import hashlib
import re

def sanitize_text(text):
    """
    Sanitizes a text
    :param text: the text to sanitize
    :return: the sanitized text
    """
    text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    text = text.replace('\n', ' ').replace('\r', '')
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    return text

def generate_user_session_id(paraphrase: str) -> str:
    """
    Generate a session id for a user
    :param paraphrase: the paraphrase
    :return: the session id
    """
    return hashlib.md5(paraphrase.encode()).hexdigest()