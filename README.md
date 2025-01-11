# Telegram Bot for Background Removal

This project is a minimalistic Telegram bot that uses the [rembg](https://github.com/danielgatis/rembg) API to remove
backgrounds from images sent by Telegram users. The bot is built with aiogram and supports a simple database for
tracking users and processed images using MariaDB.

Try this bot in action [here](https://t.me/deletebg_bot).

## Features

* Supports commands like `/start` and `/info`
* Removes the background from images sent by users
* Tracks the number of images processed per user

## Prerequisites

* Docker and Docker Compose (for containerized deployment)
* Python 3.10+ (for manual deployment)
* MariaDB database server

## Installation and Usage

Clone the repository:

```shell
git clone https://github.com/EvilFreelancer/telegram-rembg-bot.git
cd telegram-rembg-bot
```

Copy compose configuration:

```shell
cp docker-compose.dist.yml docker-compose.yml
```

Set up your environment variables by creating a `.env` file and populating it with the following:

```
# Telegram bot settings
TELEGRAM_BOT_TOKEN=5907334639:AAEi2VlsWoGo2c9mBN08tLUQZ0Mwv5MGPcs
TELEGRAM_BOT_REMBG_URL="http://rembg:7000/api/remove?url="
TELEGRAM_BOT_DB_HOSTNAME=mariadb
TELEGRAM_BOT_DB_PORT=3306
TELEGRAM_BOT_DB_DBNAME=rembg
TELEGRAM_BOT_DB_USERNAME=rembg_user
TELEGRAM_BOT_DB_PASSWORD=rembg_pass
TELEGRAM_BOT_DB_DIALECT=mariadb

# Database settings
MYSQL_ROOT_PASSWORD=root_pass
MYSQL_ROOT_HOST=%
MYSQL_DATABASE=rembg
MYSQL_USER=rembg_user
MYSQL_PASSWORD=rembg_pass
```

You need to set at least `TELEGRAM_BOT_TOKEN`, all other settings can use default values.

Start the services using Docker Compose:

```shell
docker-compose up -d
```

The bot is now running and connected to the rembg API.

**Note:**

* For GPU acceleration with rembg, configure your Docker host to support NVIDIA GPUs. Follow the instructions in
  my [post](https://dzen.ru/a/ZVt9kRBCTCGlQqyP) on setting up Linux for running and training neural networks
* Modify the `rembg` service in `docker-compose.yml` to enable GPU acceleration

## Commands

* `/start` - registers the user and displays a welcome message
* `/info` - shows the number of images processed by the user
* Upload an image to remove its background

## License

This project is licensed under the MIT License.

## Resources

* https://github.com/danielgatis/rembg
* https://t.me/deletebg_bot
* https://dzen.ru/a/ZVt9kRBCTCGlQqyP
* https://t.me/evilfreelancer
