#! /usr/bin/env python

import os
import re
import glob
import time
import numpy as np

from multiprocessing.pool import Pool
from astropy.io import fits

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def make_empty_image(imlist, nstokes=4, outname='concat.fits'):
    """
    Generate an empty dummy FITS data cube. The FITS cube can exceed available
    RAM.

    The 2D image dimensions are derived from the first cube in the list.
    The number of channels in the output cube is assumed to be the length
    of the input list of images.

    """

    with fits.open(imlist[0], memmap=True) as hud:
        xdim, ydim = np.squeeze(hud[0].data).shape[-2:]

    print("X-dimension: ", xdim)
    print("Y-dimension: ", ydim)

    zdim = int(len(imlist))
    wdim = nstokes

    dims = tuple([xdim, ydim, zdim, wdim])

    # create header
    dummy_dims = tuple(1 for d in dims)
    dummy_data = np.zeros(dummy_dims, dtype=np.float32)
    hdu = fits.PrimaryHDU(data=dummy_data)

    header = hdu.header
    for i, dim in enumerate(dims, 1):
        header["NAXIS%d" % i] = dim
        header["CRPIX1"] = int(xdim/2)
        header["CRPIX2"] = int(ydim/2)

    header.tofile(outname, overwrite=True)

    # create full-sized zero image
    header_size = len(
        header.tostring()
    )  # Probably 2880. We don't pad the header any more; it's just the bare minimum
    data_size = np.prod(dims) * np.dtype(np.float32).itemsize
    # This is not documented in the example, but appears to be Astropy's default behaviour
    # Pad the total file size to a multiple of the header block size
    block_size = 2880
    data_size = block_size * (((data_size -1) // block_size) + 1)

    with open(outname, "rb+") as f:
        f.seek(header_size + data_size - 1)
        f.write(b"\0")


def update_fits_header(cube_path, header_dict):
    # Update the header of the FITS cube
    # TODO : Fill in the header with the correct values for the entire cube
    with fits.open(cube_path, memmap=True, ignore_missing_end=True, mode="update") as hud:
        header = hud[0].header
        for key, value in header_dict.items():
            header[key] = value



def fill_cube_with_images(imlist, nstokes=4, outname='concat.fits'):
    """
    Fills the empty data cube with fits data.

    The number of channels in the output cube is assumed to be the length
    of the input list of images.
    """
    # TODO: debug: if ignore_missing_end is False, throws an error
    outhdu = fits.open(outname, memmap=True, ignore_missing_end=True, mode="update")
    outdata = outhdu[0].data


    print("Opening all images")
    fptrlist = []
    for im in imlist:
        fptrlist.append(fits.open(im, memmap=True))

    max_chan =  int(len(imlist))
    t0 = time.time()
    for ii in range(0, max_chan):
        t1 = time.time()
        print(f"Processing channel {ii}/{max_chan} in {t1 - t0}s", end='\n')
        for ss in range(nstokes):
            outdata[ss, ii, :, :] = fptrlist[ii][0].data[ss, 0, :, :]

        t0 = time.time()

    outhdu.close()
    highest_channel = int(outdata.shape[1] + 1)
    fitsheader = {
            "CRPIX3": 1, #lowestChanNo,
            "NAXIS3": highest_channel,
            "CTYPE3": ("FREQ", ""),
            }

    update_fits_header(outname, fitsheader)

    print("Closing all images")
    # Close all images
    for fptr in fptrlist:
        fptr.close()


if __name__ == '__main__':
    t = time.time()
    print("Starting fitsconcat at ", time.time())

    imlist = natural_sort(glob.glob("chan_images/uid___A002_Xf0fd41_X5f5a_target_spw_25_channel_*.fits"))

    print("making empty image")
    make_empty_image(imlist, nstokes=1)
    print("filling cube with images")
    fill_cube_with_images(imlist, nstokes=1)
    print("Ending fitsconcat at ", time.time())
    print("Elapsed time is ", time.time() - t)
