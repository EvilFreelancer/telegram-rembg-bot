import os
import asyncio
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, BigInteger, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Session
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiohttp import ClientSession

load_dotenv()

# Read settings from environment variables
REMBG_API_URL = os.getenv("TELEGRAM_BOT_REMBG_URL", "http://rembg:7000/api/remove?url=")
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_SETTINGS = {
    "dbname": os.getenv("TELEGRAM_BOT_DB_DBNAME", "rembg"),
    "username": os.getenv("TELEGRAM_BOT_DB_USERNAME", "remuser"),
    "password": os.getenv("TELEGRAM_BOT_DB_PASSWORD", "rempass"),
    "host": os.getenv("TELEGRAM_BOT_DB_HOSTNAME", "mariadb"),
    "port": os.getenv("TELEGRAM_BOT_DB_PORT", "3306"),
    "dialect": os.getenv("TELEGRAM_BOT_DB_DIALECT", "mariadb"),
}

# Initialize database
DB_URL = (
    f"{DB_SETTINGS['dialect']}://{DB_SETTINGS['username']}:{DB_SETTINGS['password']}@"
    f"{DB_SETTINGS['host']}:{DB_SETTINGS['port']}/{DB_SETTINGS['dbname']}"
    if DB_SETTINGS['dialect'] != "sqlite" else f"sqlite:///app/users.db"
)
engine = create_engine(DB_URL)
session = Session(engine)


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    """
    Users table schema
    """
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(String(255), unique=True, nullable=False)
    processed = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


# Build database schema
Base.metadata.create_all(engine)

# Initialize a bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_file_url(file_id: str) -> str:
    """
    Get file url from Telegram
    :return: File url
    """
    return f"https://api.telegram.org/file/bot{API_TOKEN}/{file_id}"


async def rembg(file_id: str) -> bytes:
    """
    Remove background from image,
    :param file_id: Unique id of file on Telegram
    :return: Bytes of downloaded image
    """
    file = await bot.get_file(file_id)
    file_url = get_file_url(file.file_path)
    async with ClientSession() as client:
        async with client.get(f"{REMBG_API_URL}{file_url}") as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception("Ошибка при удалении фона.")


@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    user = session.query(UserModel).filter_by(chat_id=str(chat_id)).first()
    if not user:
        user = UserModel(chat_id=str(chat_id))
        session.add(user)
    else:
        user.updated_at = datetime.datetime.now(datetime.UTC)
    session.commit()
    await message.answer("Привет! Этот бот удаляет фон у изображений. Просто отправь картинку!")


@dp.message(Command("info"))
async def info_command(message: Message):
    chat_id = message.chat.id
    user = session.query(UserModel).filter_by(chat_id=str(chat_id)).first()
    if user:
        await message.answer(f"Вы обработали {user.processed} изображений.")
    else:
        await message.answer("Пользователь не найден.")


@dp.message()
async def handle_image(message: Message):
    if not (message.photo or (message.document and message.document.mime_type.startswith("image"))):
        await message.answer("Это не изображение. Пожалуйста, отправьте изображение.")
        return

    chat_id = message.chat.id
    user = session.query(UserModel).filter_by(chat_id=str(chat_id)).first()
    if not user:
        user = UserModel(chat_id=str(chat_id))
        session.add(user)
    else:
        user.updated_at = datetime.datetime.now(datetime.UTC)

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id

    try:
        await bot.send_chat_action(chat_id, "upload_document")
        processed_image = await rembg(file_id)

        user.processed += 1
        session.commit()

        file_name = f"processed_{user.processed}.png"
        await message.answer_document(BufferedInputFile(processed_image, file_name))
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при обработке изображения. Попробуйте позже.")


# Start bot in pooling mode
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
