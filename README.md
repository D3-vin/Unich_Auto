# UNICH AUTO MINING BOT

<div align="center">

  <p align="center">
    <a href="https://t.me/cry_batya">
      <img src="https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram" alt="Telegram Channel">
    </a>
    <a href="https://t.me/+b0BPbs7V1aE2NDFi">
      <img src="https://img.shields.io/badge/Telegram-Chat-blue?style=for-the-badge&logo=telegram" alt="Telegram Chat">
    </a>
  </p>
</div>

## Features

- **Automatic Task Execution**
- **Daily Auto-Mining**
- **Full Parallel Account Processing**
- **Automatic Authentication**
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
   # Create a file in the data folder with accounts for authentication
   echo "your_email@example.com:password" > data/auth.txt
   
   # Create a file with accounts for mining
   echo "your_email@example.com:password" > data/farm.txt
   
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
1. **Account Authentication** - only authenticates accounts and saves tokens
2. **Mining and Reward Collection** - runs the full account processing cycle

## Key Features

- **Maximum Efficiency**: All accounts are processed simultaneously in parallel tasks for optimal performance
- **Automatic Recovery**: If an error occurs, account processing automatically restarts after a short pause
- **Proxy Rotation**: Each account is assigned its own proxy server for load distribution

## Registration/Login

- Visit [https://unich.com/en/airdrop](https://unich.com/en/airdrop/sign-up?ref=7AFR37) to register
- Register or log in to your account
- Add your account details to `data/auth.txt` in the format `email:password`
- The bot will automatically perform authentication and save the token

## Configuration

You can modify main settings in `data/config.py`:
- API key for captcha solving service
- Referral code
- Time intervals between operations
- Other parameters

Telegram http://t.me/+1fc0or8gCHsyNGFi
Thank you for visiting this repository, don't forget to contribute in the form of follows and stars. If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an issue in this GitHub repository.