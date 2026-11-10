"""Image helpers shared by the figures that embed DaVinci-rendered PNGs."""

import numpy as np


def crop_white_margin(image, threshold=248, padding=8):
    """Crop near-white margins from an image.

    Parameters
    ----------
    image : PIL.Image.Image
        Input image; converted to RGB first.
    threshold : int, default 248
        Pixels with any channel below this value count as content.
    padding : int, default 8
        Pixels of margin kept around the detected content.

    Returns
    -------
    PIL.Image.Image
        Cropped RGB image, or the RGB-converted input if it is entirely near-white.
    """
    img = image.convert("RGB")
    arr = np.asarray(img)
    mask = np.any(arr < threshold, axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(img.width, x1 + padding)
    y1 = min(img.height, y1 + padding)
    return img.crop((x0, y0, x1, y1))
