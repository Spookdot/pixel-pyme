import asyncio
import aiohttp
import validators
from PIL import ImageFont, Image
from .dict_types import MemeData, ShortMemeData
from .bounding_box import BoundingBox
from .pyme_image import PymeImage


class PymeGen:
    client: aiohttp.ClientSession

    def __init__(self):
        self.client = aiohttp.ClientSession()

    async def close(self):
        await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_memes(self) -> list[ShortMemeData]:
        resp = await self.client.get("https://spook.one/pixel/api/v1/memes")
        memes: list[ShortMemeData] = await resp.json()

        return memes

    async def make_meme(self, meme_name: str, args: list[str], font: ImageFont = None) -> PymeImage:
        if not font:
            font = ImageFont.truetype("impact.ttf", 32)

        resp = await self.client.get(f"https://spook.one/pixel/api/v1/meme?name={meme_name}")
        data: MemeData = await resp.json()

        img = await PymeImage.from_url(data["image_url"], self.client)

        for i, j in zip(args, data['parameter']):
            if validators.url(i):
                img2 = await PymeImage(i, self.client)
                for position in j['position']:
                    img.draw_image(
                        img2, BoundingBox.from_position(position))
            else:
                for position in j['position']:
                    img.draw_text(i, BoundingBox.from_position(
                        position), font=font)

        return img
