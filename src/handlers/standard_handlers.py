import json

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorCollection

from database.data_aggregator import get_aggregated_data

from utils.data_parser import parse_incoming_data


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """ Хэндлер команды /start. """
    await message.answer(text=f"Hi {message.from_user.username}!")


@router.message()
async def message_handler(
    message: Message,
    db_collection: AsyncIOMotorCollection,
) -> None:
    """ Основной хэндлер сообщений бота. """
    parsed_data = parse_incoming_data(message.text)

    if not parsed_data:
        await _send_default_response(message)
        return

    date_from, date_to, group_type = parsed_data

    result = await get_aggregated_data(
        db_collection,
        date_from,
        date_to,
        group_type,
    )

    if not result:
        await _send_default_response(message)
        return

    await message.answer(text=json.dumps(result))


async def _send_default_response(message: Message) -> None:
    """ Отправить стандартный ответ на некорректные запросы. """
    await message.answer(text="""Допустимо отправлять только следующие запросы:
    {"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-12-31T23:59:00", "group_type": "month"}
    {"dt_from": "2022-10-01T00:00:00", "dt_upto": "2022-11-30T23:59:00", "group_type": "day"}
    {"dt_from": "2022-02-01T00:00:00", "dt_upto": "2022-02-02T00:00:00", "group_type": "hour"}""")