"""
Seeing what you made, without a sign.

The ASCII output needs nothing but Python and is the fastest way to confirm
text is legible and aligned. The image output needs Pillow, which the
coolledx-driver virtualenv already has.

Always preview a file you have LOADED from disk rather than the Animation you
just built in memory -- otherwise a packing bug can hide, because the same
wrong assumption produces and consumes the data.
"""

from __future__ import annotations

from . import colors

#: One character per palette entry, chosen so lit pixels stand out from black.
ASCII_CHARS = {
    colors.BLACK: ".",
    colors.BLUE: "b",
    colors.GREEN: "g",
    colors.CYAN: "c",
    colors.RED: "r",
    colors.MAGENTA: "m",
    colors.YELLOW: "Y",
    colors.WHITE: "W",
}


def canvas_to_ascii(canvas, blank="."):
    rows = []
    for y in range(canvas.height):
        rows.append(
            "".join(
                ASCII_CHARS.get(canvas.get(x, y), "?") if canvas.get(x, y) != colors.BLACK else blank
                for x in range(canvas.width)
            )
        )
    return "\n".join(rows)


def print_frames(animation, indexes=None, label=True, columns=None):
    """Print selected frames as ASCII art. ``columns`` slices as (start, end)."""
    if indexes is None:
        indexes = range(len(animation))
    for index in indexes:
        canvas = animation[index]
        if label:
            print(f"--- frame {index} ---")
        for line in canvas_to_ascii(canvas).splitlines():
            print(line[slice(*columns)] if columns else line)
        print()


def to_images(animation, scale=7):
    """Render frames to a list of PIL images."""
    from PIL import Image

    images = []
    for canvas in animation:
        image = Image.new("RGB", (animation.width, animation.height))
        pixels = image.load()
        for x in range(animation.width):
            for y in range(animation.height):
                r, g, b = canvas.get(x, y)
                pixels[x, y] = (r * 255, g * 255, b * 255)
        images.append(
            image.resize(
                (animation.width * scale, animation.height * scale),
                Image.NEAREST,
            )
        )
    return images


def to_gif(animation, path, scale=7, loop=0):
    """Write an animated GIF at the animation's own frame delay."""
    images = to_images(animation, scale)
    if not images:
        raise ValueError("Nothing to render: no frames")
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=animation.delay,
        loop=loop,
    )
    return path


def to_sheet(animation, path, scale=4, gap=2, background=(24, 24, 32)):
    """
    Stack every frame vertically into one PNG.

    Useful for reviewing pacing at a glance, or in a terminal that cannot
    show animation.
    """
    from PIL import Image

    images = to_images(animation, scale)
    if not images:
        raise ValueError("Nothing to render: no frames")

    width = images[0].width
    height = len(images) * images[0].height + gap * (len(images) - 1)
    sheet = Image.new("RGB", (width, height), background)
    for index, image in enumerate(images):
        sheet.paste(image, (0, index * (image.height + gap)))
    sheet.save(path)
    return path
