from typing_extensions import Self
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import aiohttp
from .bounding_box import BoundingBox


class PymeImage:
    image: Image.Image

    def __init__(self, image: Image.Image):
        self.image = image

    def __getattr__(self, item):
        return getattr(self.image, item)

    @classmethod
    async def from_url(cls, url: str, client: aiohttp.ClientSession = None):
        # Open client if there isn't one provided
        if not client:
            client = aiohttp.ClientSession()
            internal_client = True
        else:
            internal_client = False

        # Download the image data
        resp = await client.get(url)
        img_data = BytesIO()

        # Write data to an in-memory buffer and open it
        async for chunk in resp.content.iter_chunked(1024):
            img_data.write(chunk)
        img = Image.open(img_data)

        # Close internal client if there is one
        if internal_client:
            client.close()

        return PymeImage(img)

    def draw_text(self, text: str, bbox: BoundingBox | tuple[int, int, int, int], font: ImageFont = None,
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

        self.draw_image(text_img, bbox)

    def draw_image(self, img: Image.Image | Self, bbox: BoundingBox | tuple[int, int, int, int]):
        if isinstance(bbox, tuple):
            bbox = BoundingBox.from_tuple(bbox)
        if isinstance(img, PymeImage):
            img = img.image

        if img.width > img.height:
            scale_factor = bbox.width / img.width
        else:
            scale_factor = bbox.height / img.height

        resized_img = img.resize((
            int(img.width * scale_factor),
            int(img.height * scale_factor)
        ))

        pos_x = bbox.left + (bbox.width - resized_img.width) // 2
        pos_y = bbox.top + (bbox.height - resized_img.height) // 2

        self.image.paste(resized_img, (pos_x, pos_y), mask=resized_img)
