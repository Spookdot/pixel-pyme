import click
import asyncio
from . import make_meme

@click.command()
@click.argument('text')
def main(text):
    asyncio.run(make_meme("anakin", [text]))
