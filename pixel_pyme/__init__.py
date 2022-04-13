from io import BytesIO
import validators
import aiohttp
from typing import TypedDict
from PIL.Image import Image, open as open_image
from PIL.ImageDraw import Draw
from PIL import ImageFont


class Position(TypedDict):
    id: int
    box_left: int
    box_top: int
    box_right: int
    box_bottom: int
    parameter_id: int

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return (self.box_left, self.box_top, self.box_right, self.box_bottom)


class Parameter(TypedDict):
    id: int
    meme_id: int
    position: list[Position]


MemeData = TypedDict('MemeData', {
                     "id": int, "name": str, "image_url": str, "parameter": list[Parameter]})

# class MemeData(TypedDict):
#id: int
#creator_id: str
#image_url: str
#server_id: str
#parameter: list[Parameter]


def draw_text(img: Image, text: str, bbox: tuple[int, int, int, int]):
    img_draw = Draw(img)
    img_draw.multiline_text(
        (bbox[0], bbox[1]), text, fill=(0, 0, 0, 255), align="center")


def draw_image(img: Image, img2: Image, bbox: tuple[int, int, int, int]):
    img.paste(img2, bbox)


async def download_image(client: aiohttp.ClientSession, url: str) -> Image:
    resp = await client.get(url)
    img_data = BytesIO()

    async for chunk in resp.content.iter_chunked(1024):
        img_data.write(chunk)

    img = open_image(img_data)
    return img


async def make_meme(meme_name: str, args: list[str]):
    async with aiohttp.ClientSession() as client:
        resp = await client.get(f"https://spook.one/pixel/api/v1/meme?name={meme_name}")
        data: MemeData = await resp.json()

        img = await download_image(client, data["image_url"])

        for i, j in zip(args, data['parameter']):
            if validators.url(i):
                img2 = await download_image(client, i)
                for position in j['position']:
                    pos = (
                        position['box_left'],
                        position['box_top'],
                        position['box_right'],
                        position['box_bottom']
                    )
                    draw_image(img, img2, pos)
            else:
                for position in j['position']:
                    pos = position.bbox
                    draw_text(img, i, pos)

    img.save(f"{meme_name}.png")
