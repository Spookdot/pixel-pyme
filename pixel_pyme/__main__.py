import aiohttp
import click
import asyncio
from PIL.Image import Image
import validators
from . import BoundingBox, download_image, draw_text, get_memes, make_meme, draw_image


@click.group()
def main():
    pass


@main.command()
@click.option("--output", "-o", help="path to output file", default="out.png")
@click.option("--input", "-i", "inp", help="Input text or url, supports multiple usage", multiple=True)
@click.argument("meme_name")
def make(meme_name, inp, output):
    loop = asyncio.get_event_loop()
    meme = loop.run_until_complete(make_meme(meme_name, inp))
    meme.save(output)


@main.command()
@click.option("--output", "-o", help="path to output file", default="out.png")
@click.option("--input", "-i", "inp", help="Text or url to image to insert", multiple=True, nargs=5)
@click.argument("image")
def draw(image, inp, output):
    async def async_draw() -> Image:
        async with aiohttp.ClientSession() as client:
            img = await download_image(client, image)
            for i in inp:
                if "." in i[1]:
                    bbox = BoundingBox.from_float_tuple(
                        (float(i[1]), float(i[2]), float(i[3]), float(i[4])),
                        img.size
                    )
                else:
                    bbox = BoundingBox.from_tuple(
                        (int(i[1]), int(i[2]), int(i[3]), int(i[4]))
                    )

                if validators.url(i[0]):
                    img2 = await download_image(client, i[0])
                    draw_image(img, img2, bbox)
                else:
                    draw_text(img, i[0], bbox)

            return img

    loop = asyncio.get_event_loop()
    img = loop.run_until_complete(async_draw())
    img.save(output)


@main.command()
def list():
    loop = asyncio.get_event_loop()
    memes = loop.run_until_complete(get_memes())
    for meme in memes:
        print(meme["name"])


if __name__ == "__main__":
    main()
