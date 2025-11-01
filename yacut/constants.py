import re
import string

ALLOWED_CHARS = string.ascii_letters + string.digits
MAX_SHORT_LENGTH = 16
ORIGINAL_LENGTH = 2048
SHORT_LENGTH = 6
GENERATED_SHORT_ATTEMPTS = 100
SHORT_PATTERN = re.compile(f"^[{re.escape(ALLOWED_CHARS)}]+$")
RESERVED_SHORTS = ["files"]
ALLOWED_FILES = ["jpg", "jpeg", "png", "gif", "pdf", "txt"]
MAX_FILE_SIZE = 10 * 1024 * 1024
AUTH_HEADER = "OAuth {}"
REDIRECT_ENPOINT = 'main.redirect_to_url'
