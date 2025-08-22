from typing import Dict, Tuple

# API key for captcha solving service
API_KEY_2CAPTCHA: str = "api"  # Replace with your 2Captcha key

# Referral program settings
REF_CODE: str = "7AFR37"  # Default referral code

# Parallel processing settings
MAX_CONCURRENCY: int = 0  # 0 - no limit on parallel tasks

# Time intervals
CYCLE_INTERVAL: int = 24 * 60 * 60  # Time between cycles in seconds (24 hours)
REQUEST_DELAY: Tuple[float, float] = (1, 3)  # Range of delay between requests (min, max) in seconds

# Captcha settings
CAPTCHA_MAX_ATTEMPTS: int = 3  # Maximum attempts to solve captcha

# File paths
DATA_DIR: str = "data"
FILES: Dict[str, str] = {
    "accounts_json": "accounts.json",  # File for storing account tokens
    "accounts_txt": "accounts.txt",    # File with accounts
    "proxy_txt": "proxy.txt"           # File with proxy servers
} 