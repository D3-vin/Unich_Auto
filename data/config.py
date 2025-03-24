from typing import Dict, Tuple

# API key for captcha solving service
API_KEY_2CAPTCHA: str = "key"  # Replace with your 2Captcha key

# Referral program settings
REF_CODE: str = "7AFR37"  # Default referral code

# Parallel processing settings
MAX_CONCURRENCY: int = 0  # 0 - no limit on parallel tasks

# Time intervals
CYCLE_INTERVAL: int = 24 * 60 * 60  # Time between cycles in seconds (24 hours)
REQUEST_DELAY: Tuple[float, float] = (1, 3)  # Range of delay between requests (min, max) in seconds

# API endpoints
ENDPOINTS: Dict[str, str] = {
    "site_url": "https://unich.com/en/airdrop/sign-in",
    "captcha_id": "e7baa772ac1ae5dceccd7273ad5f57bd",
    "auth_url": "https://api.unich.com/airdrop/user/v1/auth/sign-in",
    "mining_start_url": "https://api.unich.com/airdrop/user/v1/mining/start",
    "social_list_url": "https://api.unich.com/airdrop/user/v1/social/list-by-user",
    "mining_recent_url": "https://api.unich.com/airdrop/user/v1/mining/recent",
    "ref_url": "https://api.unich.com/airdrop/user/v1/ref",
    "add_ref_url": "https://api.unich.com/airdrop/user/v1/ref/refer-sign-up",
    "social_claim_url": "https://api.unich.com/airdrop/user/v1/social/claim/"
}

# File paths
DATA_DIR: str = "data"
FILES: Dict[str, str] = {
    "accounts_json": "accounts.json",  # File for storing account tokens
    "auth_txt": "auth.txt",           # File with accounts for authentication
    "farm_txt": "farm.txt",           # File with accounts for mining
    "proxy_txt": "proxy.txt"          # File with proxy servers
} 