from io import BytesIO
import validators
import aiohttp
from typing import TypedDict
from PIL import ImageFont, Image, ImageDraw


Position = TypedDict('Position', {
    'box_left': int, 'box_top': int, 'box_right': int, 'box_bottom': int, 'id': int, 'parameter_id': int
})

Parameter = TypedDict('Parameter', {
    'id': int, 'meme_id': int, 'name': str, 'position': list[Position]
})

MemeData = TypedDict('MemeData', {
    "id": int, "name": str, "image_url": str, "parameter": list[Parameter]
})

ShortMemeData = TypedDict("ShortMemeData", {
    "id": int, "name": str, "image_url": str, "creator_id": str, "server_id": str
})


class BoundingBox:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __getitem__(self, key) -> int:
        return self.into_tuple()[key]

    def __setitem__(self, key, value):
        match key:
            case 0:
                self.left = value
            case 1:
                self.top = value
            case 2:
                self.right = value
            case 3:
                self.bottom = value
            case _:
                raise IndexError("Invalid index")

    @classmethod
    def from_position(cls, pos: Position):
        return cls(pos['box_left'], pos['box_top'], pos['box_right'], pos['box_bottom'])

    @classmethod
    def from_tuple(cls, tup: tuple[int, int, int, int]):
        return cls(tup[0], tup[1], tup[2], tup[3])

    @classmethod
    def from_float_tuple(cls, tup: tuple[float, float, float, float], size: tuple[int, int]):
        return cls(int(tup[0] * size[0]), int(tup[1] * size[1]), int(tup[2] * size[0]), int(tup[3] * size[1]))

    def into_tuple(self) -> tuple[int, int, int, int]:
        return self.left, self.top, self.right, self.bottom

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


def draw_text(img: Image.Image, text: str, bbox: BoundingBox | tuple[int, int, int, int], font: ImageFont = None,
              fill: tuple[int, int, int, int] = (255, 255, 255, 255), align: str = "center", stroke_width: int = 2,
              stroke_fill: tuple[int, int, int, int] = (0, 0, 0, 255)):
    if not font:
        font = ImageFont.truetype("impact.ttf", 32)

    text_img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    img_draw = ImageDraw.Draw(text_img)

    text_size = img_draw.textsize(text, font=font)
    text_img = text_img.resize((text_size[0] + 6, text_size[1] + 10))
    img_draw = ImageDraw.Draw(text_img)

    img_draw.multiline_text(
        (3, 1), text, fill=fill, align=align, font=font, stroke_width=stroke_width, stroke_fill=stroke_fill
    )

    draw_image(img, text_img, bbox)


def draw_image(img: Image.Image, img2: Image.Image, bbox: BoundingBox | tuple[int, int, int, int]):
    if isinstance(bbox, tuple):
        bbox = BoundingBox.from_tuple(bbox)

    if img2.width > img2.height:
        scale_factor = bbox.width / img2.width
    else:
        scale_factor = bbox.height / img2.height

    resized_img = img2.resize((
        int(img2.width * scale_factor),
        int(img2.height * scale_factor)
    ))

    pos_x = bbox.left + (bbox.width - resized_img.width) // 2
    pos_y = bbox.top + (bbox.height - resized_img.height) // 2

    img.paste(resized_img, (pos_x, pos_y), mask=resized_img)


async def download_image(client: aiohttp.ClientSession, url: str) -> Image.Image:
    resp = await client.get(url)
    img_data = BytesIO()

    async for chunk in resp.content.iter_chunked(1024):
        img_data.write(chunk)

    img = Image.open(img_data)
    return img


async def get_memes() -> list[ShortMemeData]:
    async with aiohttp.ClientSession() as client:
        resp = await client.get("https://spook.one/pixel/api/v1/memes")
        memes: list[ShortMemeData] = await resp.json()

        return memes


async def make_meme(meme_name: str, args: list[str], font: ImageFont = None) -> Image.Image:
    if not font:
        font = ImageFont.truetype("impact.ttf", 32)

    async with aiohttp.ClientSession() as client:
        resp = await client.get(f"https://spook.one/pixel/api/v1/meme?name={meme_name}")
        data: MemeData = await resp.json()

        img = await download_image(client, data["image_url"])

        for i, j in zip(args, data['parameter']):
            if validators.url(i):
                img2 = await download_image(client, i)
                for position in j['position']:
                    draw_image(img, img2, BoundingBox.from_position(position))
            else:
                for position in j['position']:
                    draw_text(img, i, BoundingBox.from_position(
                        position), font=font)

    return img
