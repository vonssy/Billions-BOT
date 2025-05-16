from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
from colorama import *
import asyncio, time, json, base64, os, re, pytz

wib = pytz.timezone('Asia/Jakarta')

class BillionsNetwork:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://signup.billions.network",
            "Referer": "https://signup.billions.network/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://signup-backend.billions.network"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Billions Network - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def normalize_iso_format(self, next_daily_reward: str):
        date_str = next_daily_reward.replace("Z", "+00:00")

        match = re.match(r"(.*\.\d{1,6})(\+00:00)", date_str)
        if match:
            timestamp, offset = match.groups()
            if '.' in timestamp:
                seconds, micros = timestamp.split('.')
                micros = micros.ljust(6, '0')
                date_str = f"{seconds}.{micros}{offset}"

        return datetime.fromisoformat(date_str)
    
    def get_token(self, session_id: str):
        try:
            token = session_id.replace("session_id=", "")

            return token
        except Exception as e:
            return None
        
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            exp_time = parsed_payload["exp"]
            
            return exp_time
        except Exception as e:
            return None
        
    def check_token_status(self, token: str):
        try:
            exp_time = self.decode_token(token)
            now = int(time.time())

            if now > exp_time:
                return False

            return True
        except Exception as e:
            return False
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
        mask_account = local[:6] + '*' * 6 + local[-6:]
        return mask_account
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=self.BASE_API, headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_data(self, session_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/me"
        headers = {
            **self.headers,
            "Cookie": session_id
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def claim_daily_reward(self, session_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/claim-daily-reward"
        headers = {
            **self.headers,
            "Content-Length": "0",
            "Cookie": session_id
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def process_check_connection(self, session_id: str, token: str, use_proxy: bool, rotate_proxy: bool):
        is_token_active = self.check_token_status(token)
        if not is_token_active:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Session Id:{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {self.mask_account(token)} {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Expired{Style.RESET_ALL}"
            )
            return False
        
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(session_id) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(session_id) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )

                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK {Style.RESET_ALL}          "
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )

        return True
        
    async def process_accounts(self, session_id: str, token: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(session_id, token, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(session_id) if use_proxy else None

            user = await self.user_data(session_id, proxy)
            if not user:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET User Data Failed {Style.RESET_ALL}"
                )
                return

            email = user.get("email", "Unknown")
            power = user.get("power", 0)

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Account :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Power   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {power} PTS {Style.RESET_ALL}"
            )
            
            next_daily_reward = user.get("nextDailyRewardAt", None)
            if next_daily_reward is None:
                claim = await self.claim_daily_reward(session_id, proxy)
                if claim:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}25 Power PTS{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Claim Failed {Style.RESET_ALL}"
                    )
            else:
                utc_now = datetime.now(timezone.utc)
                next_daily_reward_utc = self.normalize_iso_format(next_daily_reward)

                if utc_now >= next_daily_reward_utc:
                    claim = await self.claim_daily_reward(session_id, proxy)
                    if claim:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}25 Power PTS{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Claim Failed {Style.RESET_ALL}"
                        )
                else:
                    next_daily_reward_wib = next_daily_reward_utc.astimezone(wib).strftime('%x %X %Z')
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Not Time To Claim {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Claim At: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{next_daily_reward_wib}{Style.RESET_ALL}"
                    )

    async def main(self):
        try:
            with open('cookies.txt', 'r') as file:
                session_ids = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(session_ids)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 26
                for idx, session_id in enumerate(session_ids, 1):
                    if session_id:
                        token = self.get_token(session_id)

                        if token:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {len(session_ids)} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                            )
                            await self.process_accounts(session_id, token, use_proxy, rotate_proxy)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*63)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = BillionsNetwork()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Billions Network - BOT{Style.RESET_ALL}                                       "                              
        )