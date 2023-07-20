import io
import xml.etree.ElementTree as ET

import defusedxml  # type: ignore[import]
from aiogram import Bot, Dispatcher, executor, types  # type: ignore[import]

API_TOKEN = ""

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_text_without_html_tags(text: str) -> str:
    return "".join(ET.fromstring(text).itertext())


@dp.message_handler()
async def clear_html_tags_handler(message: types.Message):
    if message.document is None:
        await message.answer("Send me a txt file")
        return

    ext = message.document.file_name.split(".")[-1]
    if ext != "txt":
        await message.answer("Only .txt files are supported")
        return

    file = await message.document.download(destination_file=io.BytesIO())
    try:
        no_html_tags = get_text_without_html_tags(file.read().decode("utf-8"))
    except ET.ParseError:
        await message.answer("Invalid HTML file")
    else:
        await message.answer_document(
            types.InputFile(
                io.BytesIO(no_html_tags.encode("utf-8")),
                filename=message.document.file_name,
            )
        )


if __name__ == "__main__":
    defusedxml.defuse_stdlib()
    executor.start_polling(dp, skip_updates=True)
