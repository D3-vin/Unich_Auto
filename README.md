# 🚀 UNICH Bot - Automation for UNICH

## 📢 Connect with Us

- **📢 Channel**: [https://t.me/D3_vin](https://t.me/D3_vin) - Latest updates and releases
- **💬 Chat**: [https://t.me/D3vin_chat](https://t.me/D3vin_chat) - Community support and discussions
- **📁 GitHub**: [https://github.com/D3-vin](https://github.com/D3-vin) - Source code and development

## ✨ Key Features

- **Automatic Task Execution**
- **Daily Auto-Mining**
- **Full Parallel Account Processing**
- **Automatic Authentication & Re-Authentication**
- **Proxy Management System**

## Requirements

- **Python 3.7+**: Make sure you have Python version 3.7 or higher installed
- **Additional Libraries**: All required dependencies are listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TellBip/Unich_Auto.git
   cd unich-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Prepare configuration files:
   ```bash
   # Create a file in the data folder with your accounts
   echo "your_email@example.com:password" > data/accounts.txt
   
   # For proxy usage (optional)
   echo "ip:port" > data/proxy.txt
   # or
   echo "ip:port:user:password" > data/proxy.txt
   ```

## Running the Program

Start the bot with:
```bash
python main.py
```

After starting, you can choose the operation mode:
1. **Mining and Reward Collection** - runs the full account processing cycle
2. **Exit** - closes the program

## Key Features

- **Maximum Efficiency**: All accounts are processed simultaneously in parallel tasks for optimal performance
- **Automatic Recovery**: If an error occurs, account processing automatically restarts after a short pause
- **Proxy Rotation**: Each account is assigned its own proxy server for load distribution
- **Token Re-Authentication**: Automatically re-authenticates accounts when tokens expire

## Registration/Login

- Visit [https://unich.com/en/airdrop](https://unich.com/en/airdrop/sign-up?ref=7AFR37) to register
- Register or log in to your account
- Add your account details to `data/accounts.txt` in the format `email:password`
- The bot will automatically perform authentication and save the token

## Configuration

You can modify main settings in `data/config.py`:
- API key for captcha solving service
- Referral code
- Time intervals between operations
- Other parameters

Telegram http://t.me/+1fc0or8gCHsyNGFi
Thank you for visiting this repository, don't forget to contribute in the form of follows and stars. If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an issue in this GitHub repository.