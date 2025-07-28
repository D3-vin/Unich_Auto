import json
import time
import random
import asyncio
import os
from twocaptcha import TwoCaptcha
from curl_cffi import requests
from datetime import datetime
from colorama import Fore, Style, init

# Import settings from data/config.py
from data.config import (
    API_KEY_2CAPTCHA, 
    REF_CODE, 
    MAX_CONCURRENCY, 
    CYCLE_INTERVAL, 
    REQUEST_DELAY, 
    DATA_DIR, 
    FILES
)

# Initialize colorama for Windows
init(autoreset=True)

class HTTPClient:
    """Base HTTP client for making requests"""
    
    def __init__(self, proxy=None):
        self.session = self._create_session(proxy)
        self.current_proxy = proxy
        
    def _create_session(self, proxy=None):
        """Create and configure session"""
        session = requests.Session()
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})
        
        if proxy:
            if not proxy.startswith(("http://", "https://")):
                proxy = f"http://{proxy}"
            session.proxies.clear()
            session.proxies.update({"http": proxy, "https": proxy})
            
        return session
    
    def _create_auth_session(self, token, proxy=None):
        """Create authenticated session with token"""
        session = self._create_session(proxy)
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    async def _make_request(self, method, url, **kwargs):
        """Make HTTP request with error handling and print proxy info for debug"""
        proxy_info = self.session.proxies.get('http') or self.session.proxies.get('https')
        #print(f"[HTTPClient] Sending {method.upper()} request to {url} via proxy: {proxy_info}")
        try:
            response = getattr(self.session, method.lower())(url, **kwargs)
            if 200 <= response.status_code < 300:
                return True, response.json()
            return False, response.text
        except Exception as e:
            return False, str(e)

class Unich:
    def __init__(self) -> None:
        # API endpoints
        self.endpoints = {
            "site_url": "https://unich.com/en/airdrop/sign-in",
            "sitekey": "6LdEl4grAAAAAB8fg8oGNPZhhcUbR4uuM8VQI0H0",
            "auth_url": "https://api.unich.com/airdrop/user/v1/auth/sign-in",
            "mining_start_url": "https://api.unich.com/airdrop/user/v1/mining/start",
            "social_list_url": "https://api.unich.com/airdrop/user/v1/social/list-by-user",
            "mining_recent_url": "https://api.unich.com/airdrop/user/v1/mining/recent",
            "ref_url": "https://api.unich.com/airdrop/user/v1/ref",
            "add_ref_url": "https://api.unich.com/airdrop/user/v1/ref/refer-sign-up",
            "social_claim_url": "https://api.unich.com/airdrop/user/v1/social/claim/"
        }
        
        self.site_url = self.endpoints["site_url"]
        self.sitekey = self.endpoints["sitekey"]
        self.auth_url = self.endpoints["auth_url"]
        self.mining_start_url = self.endpoints["mining_start_url"]
        self.social_list_url = self.endpoints["social_list_url"]
        self.mining_recent_url = self.endpoints["mining_recent_url"]
        self.ref_url = self.endpoints["ref_url"]
        self.add_ref_url = self.endpoints["add_ref_url"]
        self.social_claim_url = self.endpoints["social_claim_url"]
        
        # File paths
        self.data_dir = DATA_DIR
        self.accounts_json = os.path.join(self.data_dir, FILES["accounts_json"])
        self.accounts_txt = os.path.join(self.data_dir, FILES["accounts_txt"])
        self.proxy_txt = os.path.join(self.data_dir, FILES["proxy_txt"])
        
        # Create data directory if it doesn't exist
        self.ensure_data_dir()
        
        self.request_delay = REQUEST_DELAY
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        
        # Initialize 2Captcha
        self.solver = TwoCaptcha(API_KEY_2CAPTCHA)
        
        # Initialize HTTP client
        self.http_client = HTTPClient()

    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            self.log(f"{Fore.GREEN}Created directory {self.data_dir} for configuration files{Style.RESET_ALL}")

    def log(self, message):
        """Logging with formatting and timestamp"""
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%H:%M:%S')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def print_account_message(self, email, proxy, color, message):
        """Formatted output of account processing messages"""
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {email} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy or 'None'}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def welcome(self):
        """Display welcome message"""
        telegram_link = "https://t.me/+1fc0or8gCHsyNGFi"
        print(f"""
        {Fore.GREEN + Style.BRIGHT}
        U   U N   N IIIII  CCCC H   H
        U   U NN  N   I   C     H   H
        U   U N N N   I   C     HHHHH
        U   U N  NN   I   C     H   H
        UUUUU N   N IIIII  CCCC H   H
        {Style.RESET_ALL}
{Fore.GREEN + Style.BRIGHT}Developed by: @Tell_Bip{Style.RESET_ALL}
{Fore.GREEN + Style.BRIGHT}Our Telegram channel:{Style.RESET_ALL} {Fore.BLUE + Style.BRIGHT}\x1b]8;;{telegram_link}\x07{telegram_link}\x1b]8;;\x07{Style.RESET_ALL}
        """)

    def load_accounts(self, mode="farm"):
        """Load accounts from file based on operation mode
        
        Args:
            mode: Operation mode - always "farm" after menu change
        """
        filename = self.accounts_txt
        accounts = []
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File '{filename}' not found.{Style.RESET_ALL}")
                return []
                
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line and ":" in line:
                        email, password = line.split(":", 1)
                        accounts.append({"email": email.strip(), "password": password.strip()})
            
            self.log(f"{Fore.GREEN}Loaded {len(accounts)} accounts from {filename}{Style.RESET_ALL}")
            return accounts
        except Exception as e:
            self.log(f"{Fore.RED}Error reading accounts file: {str(e)}{Style.RESET_ALL}")
            return []

    async def load_proxies(self):
        """Load proxies from file"""
        try:
            if not os.path.exists(self.proxy_txt):
                self.log(f"{Fore.RED}File '{self.proxy_txt}' not found.{Style.RESET_ALL}")
                return
                
            with open(self.proxy_txt, "r") as file:
                self.proxies = [line.strip() for line in file if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED}No proxies found in file {self.proxy_txt}{Style.RESET_ALL}")
                return
                
            self.log(f"{Fore.GREEN}Loaded {len(self.proxies)} proxies{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED}Error reading proxy file: {str(e)}{Style.RESET_ALL}")

    def check_proxy_schemes(self, proxy):
        """Check proxy scheme and add http:// if needed"""
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy.startswith(scheme) for scheme in schemes):
            return proxy
        return f"http://{proxy}"

    def get_next_proxy_for_account(self, email):
        """Get proxy for specific account"""
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        """Rotate proxy for account"""
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def read_tokens_json(self):
        """Read tokens from JSON file"""
        try:
            if not os.path.exists(self.accounts_json):
                return {}
            
            with open(self.accounts_json, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            self.log(f"{Fore.RED}Error reading tokens JSON file: {str(e)}{Style.RESET_ALL}")
            return {}

    def get_tokens_by_emails(self, emails):
        """Get tokens by email list"""
        tokens = {}
        account_tokens = self.read_tokens_json()
        
        for email in emails:
            if email in account_tokens:
                tokens[email] = account_tokens[email]
        
        return tokens

    def save_token_json(self, email, token):
        """Save token to JSON file"""
        try:
            # Load existing data or create new dictionary
            if os.path.exists(self.accounts_json):
                with open(self.accounts_json, "r") as file:
                    accounts_data = json.load(file)
            else:
                accounts_data = {}
            
            # Update token for this email
            accounts_data[email] = token
            
            # Save back to file
            with open(self.accounts_json, "w") as file:
                json.dump(accounts_data, file, indent=4)
                
            self.print_account_message(email, None, Fore.GREEN, f"Token saved to {self.accounts_json}")
            return True
        except Exception as e:
            self.print_account_message(email, None, Fore.RED, f"Error saving token: {str(e)}")
            return False

    def save_success(self, email, password, access_token):
        """Save successful authentication"""
        try:
            # Save token to JSON
            self.save_token_json(email, access_token)
            return True
        except Exception as e:
            self.log(f"{Fore.RED}Error saving result to file: {str(e)}{Style.RESET_ALL}")
            return False

    async def async_delay(self):
        """Asynchronous delay between requests"""
        delay = random.uniform(self.request_delay[0], self.request_delay[1])
        await asyncio.sleep(delay)

    async def start_mining(self, token, proxy=None):
        """Start mining"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return await self.http_client._make_request("post", self.mining_start_url, json={}, impersonate="chrome")

    async def get_social_list(self, token, proxy=None):
        """Get social tasks list"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return await self.http_client._make_request("get", self.social_list_url, impersonate="chrome")

    async def get_recent_mining(self, token, proxy=None):
        """Get mining data"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return await self.http_client._make_request("get", self.mining_recent_url, impersonate="chrome")

    async def get_ref(self, token, proxy=None):
        """Get referral information"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return await self.http_client._make_request("get", self.ref_url, impersonate="chrome")
        

    async def add_ref(self, token, ref_code=REF_CODE, proxy=None):
        """Add referral code"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return await self.http_client._make_request("post", self.add_ref_url, json={"code": ref_code}, impersonate="chrome")

    async def claim_social_reward(self, token, task_id, proxy=None):
        """Claim social task reward"""
        if proxy:
            self.http_client.session = self.http_client._create_session(proxy)
        self.http_client.session.headers.update({"Authorization": f"Bearer {token}"})
        url = f"{self.social_claim_url}{task_id}"
        return await self.http_client._make_request("post", url, json={"evidence": task_id}, impersonate="chrome")

    async def process_account_async(self, email, token, proxy=None):
        """Asynchronous processing of one account with token"""
        try:
            self.print_account_message(email, proxy, Fore.CYAN, "Processing account")

            # Check mining status
            mining_success, mining_data = await self.get_recent_mining(token, proxy)
            
            # Check for unauthorized error and re-authenticate if needed
            unauthorized = False
            if not mining_success:
                # Print the raw response for debugging
                #self.print_account_message(email, proxy, Fore.YELLOW, f"Mining status response: {mining_data}")
                
                # Check multiple possible formats of the unauthorized error
                if isinstance(mining_data, dict) and mining_data.get("code") == "UNAUTHORIZED":
                    unauthorized = True
                elif isinstance(mining_data, str) and "UNAUTHORIZED" in mining_data:
                    unauthorized = True
                elif isinstance(mining_data, str) and "Unauthorized" in mining_data:
                    unauthorized = True
                
            if unauthorized:
                self.print_account_message(email, proxy, Fore.YELLOW, "Token expired, attempting re-authentication")
                
                # Get account details from stored accounts
                account_data = None
                accounts = self.load_accounts()
                for acc in accounts:
                    if acc["email"] == email:
                        account_data = acc
                        break
                
                if account_data:
                    # Re-authenticate account
                    auth_success, new_token = await self.auth_account_async(account_data, proxy)
                    if auth_success and new_token:
                        self.print_account_message(email, proxy, Fore.GREEN, "Re-authentication successful")
                        token = new_token  # Update token
                        # Save the new token
                        self.save_token_json(email, new_token)
                        # Retry getting mining status with new token
                        mining_success, mining_data = await self.get_recent_mining(token, proxy)
                    else:
                        self.print_account_message(email, proxy, Fore.RED, "Re-authentication failed")
                        return  # Exit early if re-auth failed
                else:
                    self.print_account_message(email, proxy, Fore.RED, "Account data not found for re-authentication")
                    return  # Exit early
            
            if mining_success and isinstance(mining_data, dict):
                mining_info = mining_data.get("data", {})
                is_mining = mining_info.get("isMining", False)
                balance = mining_info.get("mUn", 0)
                daily_reward = mining_info.get("miningDailyReward", 0)
                next_mining = mining_info.get("nextMining", "")
                
                self.print_account_message(
                    email, proxy, Fore.CYAN, 
                    f"Mining status: {'Active' if is_mining else 'Inactive'}, "
                    f"Balance: {balance} mUn, "
                    f"Daily reward: {daily_reward} mUn"
                )
                
                if not is_mining:
                    self.print_account_message(email, proxy, Fore.CYAN, "Starting mining")
                    start_success, _ = await self.start_mining(token, proxy)
                    if start_success:
                        self.print_account_message(email, proxy, Fore.GREEN, "Mining successfully started")
                    await self.async_delay()
            else:
                self.print_account_message(email, proxy, Fore.RED, f"Failed to get mining status: {mining_data}")
                return  # Exit if we couldn't get mining status
                
            # Check referral information and valid
            ref_success, ref_data = await self.get_ref(token, proxy)
            # Check for unauthorized error and exit since we've already tried re-auth
            if not ref_success and isinstance(ref_data, dict) and ref_data.get("code") == "UNAUTHORIZED":
                self.print_account_message(email, proxy, Fore.RED, "Token unauthorized for referral check")
                return
                
            if ref_success and isinstance(ref_data, dict):
                ref_info = ref_data.get("data", {}).get("referrer", {})
                current_ref_code = ref_info.get("refCode")
                
                if not ref_info.get("referred", False):
                    self.print_account_message(email, proxy, Fore.CYAN, f"Adding referral code {REF_CODE}")
                    await self.add_ref(token, proxy=proxy)
                    await self.async_delay()
                else:
                    self.print_account_message(email, proxy, Fore.GREEN, f"Referral code {current_ref_code} already added")

            # Get and process social tasks
            social_success, social_data = await self.get_social_list(token, proxy)
            # Check for unauthorized error and exit since we've already tried re-auth
            if not social_success and isinstance(social_data, dict) and social_data.get("code") == "UNAUTHORIZED":
                self.print_account_message(email, proxy, Fore.RED, "Token unauthorized for social tasks")
                return
                
            if social_success and isinstance(social_data, dict):
                tasks_data = social_data.get("data", {}).get("items", [])
                unclaimed_tasks = [task for task in tasks_data if not task.get("claimed", False)]
                
                if unclaimed_tasks:
                    self.print_account_message(email, proxy, Fore.CYAN, f"Found {len(unclaimed_tasks)} unclaimed tasks")
                    
                    for task in unclaimed_tasks:
                        task_id = task["id"]
                        task_title = task["title"]
                        task_reward = task["pointReward"]
                        self.print_account_message(email, proxy, Fore.CYAN, f"Processing task: {task_title} (Reward: {task_reward} points)")
                        
                        claim_success, _ = await self.claim_social_reward(token, task_id, proxy)
                        if claim_success:
                            self.print_account_message(email, proxy, Fore.GREEN, f"Successfully claimed reward for: {task_title}")
                        await self.async_delay()
                else:
                    self.print_account_message(email, proxy, Fore.GREEN, "All social tasks have been completed")
            else:
                self.print_account_message(email, proxy, Fore.YELLOW, "Failed to get social tasks list")
            
            self.print_account_message(
                email, proxy, Fore.YELLOW, 
                f"Processing completed. Next cycle in {CYCLE_INTERVAL // 3600} hours"
            )
            
        except Exception as e:
            self.print_account_message(email, proxy, Fore.RED, f"Error: {str(e)}")
            self.print_account_message(email, proxy, Fore.YELLOW, "Retrying in 1 minute")
            await asyncio.sleep(60)  # Wait a minute on error

    async def auth_account_async(self, account, proxy=None):
        """Asynchronous authentication"""
        try:
            email = account['email']
            self.print_account_message(email, proxy, Fore.CYAN, "Authenticating account")
            
            # Create session with proxy
            session = self.http_client._create_session(proxy)
            
            # Send captcha for solving (synchronously as library doesn't support async)
            self.print_account_message(email, proxy, Fore.CYAN, "Solving captcha")
            result = self.solver.recaptcha(sitekey=self.sitekey, url=self.site_url)
            print(result)
            # Parse JSON string from result['code']
            captcha_token = result['code']
            
            json = {
                "email": account['email'],
                "password": account['password'],
                "g-recaptcha-response": captcha_token
            }

            # Send authentication request with curl_cffi
            self.print_account_message(email, proxy, Fore.CYAN, "Sending authentication request")
            response = session.post(self.auth_url, json=json, impersonate="chrome")
            
            # Check response status (2xx is considered successful)
            if 200 <= response.status_code < 300:
                result_data = response.json()
                
                # Check for tokens in response
                if "data" in result_data and "accessToken" in result_data["data"]:
                    access_token = result_data["data"]["accessToken"]
                    self.print_account_message(email, proxy, Fore.GREEN, "Access token received")
                    
                    # Save token to accounts.json
                    self.save_success(email, account["password"], access_token)
                    
                    # Additional information if available
                    if "mUn" in result_data["data"]:
                        balance = result_data["data"]["mUn"]
                        self.print_account_message(email, proxy, Fore.GREEN, f"Current balance: {balance} mUn")
                    
                    return True, access_token
                
                return False, None
            else:
                self.print_account_message(email, proxy, Fore.RED, f"Authentication error: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.print_account_message(email, proxy, Fore.RED, f"Error during authentication: {str(e)}")
            return False, None

    def print_menu(self):
        """Display operation mode selection menu"""
        print(f"{Fore.CYAN + Style.BRIGHT}Select operation mode:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Mining and Reward Collection")
        print(f"2. Exit{Style.RESET_ALL}")
        
        while True:
            try:
                choice = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter number [1/2]: {Style.RESET_ALL}"))
                if choice == 1:
                    return "farm"
                elif choice == 2:
                    self.log(f"{Fore.GREEN}Exiting program{Style.RESET_ALL}")
                    exit(0)
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter 1 or 2{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Please enter a number.{Style.RESET_ALL}")

    async def process_all_accounts_async(self, mode="farm"):
        """Main asynchronous function that starts processing all accounts"""
        while True:
            try:
                # Read accounts and proxies
                accounts = self.load_accounts()
                await self.load_proxies()
                
                if not accounts:
                    self.log(f"{Fore.RED + Style.BRIGHT}No accounts found in file {self.accounts_txt}{Style.RESET_ALL}")
                    await asyncio.sleep(300)  # Wait 5 minutes and try again
                    continue
                
                # Get tokens for accounts
                email_to_token = self.get_tokens_by_emails([acc["email"] for acc in accounts])
                
                # List of tasks for asynchronous execution
                processing_tasks = []
                auth_tasks = []
                
                # First, count total accounts and log the start
                total_accounts = len(accounts)
                self.log(f"{Fore.CYAN}Starting parallel processing of {total_accounts} accounts{Style.RESET_ALL}")
                
                # Prepare tasks for accounts with and without tokens
                for account in accounts:
                    email = account["email"]
                    proxy = self.get_next_proxy_for_account(email)
                    
                    # If account already has token, add to processing tasks
                    if email in email_to_token:
                        token = email_to_token[email]
                        self.print_account_message(email, proxy, Fore.GREEN, "Token found in cache")
                        processing_tasks.append((email, token, proxy))
                    else:
                        # If no token, prepare for authentication
                        self.print_account_message(email, proxy, Fore.YELLOW, "Token not found, waiting for authentication")
                        # Add to auth tasks
                        auth_tasks.append((account, proxy))
                
                # Process authentication tasks in parallel
                if auth_tasks:
                    self.log(f"{Fore.CYAN}Authenticating {len(auth_tasks)} accounts in parallel{Style.RESET_ALL}")
                    
                    # Create coroutines for all auth tasks
                    auth_coroutines = [self.auth_account_async(account, proxy) for account, proxy in auth_tasks]
                    
                    # Run all authentications in parallel
                    auth_results = await asyncio.gather(*auth_coroutines, return_exceptions=True)
                    
                    # Process auth results and add successful ones to processing tasks
                    for i, result in enumerate(auth_results):
                        account, proxy = auth_tasks[i]
                        email = account["email"]
                        
                        if isinstance(result, Exception):
                            self.print_account_message(email, proxy, Fore.RED, f"Authentication error: {str(result)}")
                        else:
                            success, token = result
                            if success and token:
                                self.print_account_message(email, proxy, Fore.GREEN, "Authentication successful")
                                processing_tasks.append((email, token, proxy))
                            else:
                                self.print_account_message(email, proxy, Fore.RED, "Authentication failed")
                
                # Create processing coroutines
                process_coroutines = [self.process_account_async(email, token, proxy) for email, token, proxy in processing_tasks]
                
                # If no tasks, wait and try again
                if not process_coroutines:
                    self.log(f"{Fore.YELLOW}No accounts to process. Retrying in 5 minutes.{Style.RESET_ALL}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
                    continue
                
                # Start all processing tasks simultaneously
                self.log(f"{Fore.CYAN}Starting mining for {len(process_coroutines)} accounts in parallel{Style.RESET_ALL}")
                await asyncio.gather(*process_coroutines)
                
                # Wait for next cycle
                self.log(f"{Fore.CYAN}Waiting {CYCLE_INTERVAL // 3600} hours before next cycle{Style.RESET_ALL}")
                await asyncio.sleep(CYCLE_INTERVAL)
                
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Global error: {str(e)}{Style.RESET_ALL}")
                await asyncio.sleep(60)  # Wait a minute on error

    async def main(self):
        """Main bot startup method"""
        try:
            self.welcome()
            
            # Check for data directory
            self.ensure_data_dir()
            
            # Select operation mode
            mode = self.print_menu()
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}Starting Unich bot in mining mode{Style.RESET_ALL}")
            await self.process_all_accounts_async(mode)
            
            self.log(f"{Fore.GREEN + Style.BRIGHT}Bot operation completed.{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Program stopped by user{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Critical error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        # Create and start bot
        async def run():
            bot = Unich()
            await bot.main()
            
        # Run async code
        asyncio.run(run())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW + Style.BRIGHT}Program stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Critical error: {str(e)}{Style.RESET_ALL}")