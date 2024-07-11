#! /usr/bin/env python


import glob
import time

from casatools import image
ia = image()


def imconcat_virtual(image_suffix='image', outname='concat.image'):
    t1 = time.time()
    imagenames = sorted(glob.glob(f'chan_images/uid*.{image_suffix}'))

    outia = ia.imageconcat(outfile=outname, infiles=imagenames, mode='movevirtual', relax=True, axis=2, overwrite=True)
    outia.close()
    outia.done()

    t2 = time.time()
    print(f'Elapsed time is {t2-t1:.2f}s')


if __name__ == '__main__':
    imconcat_virtual()
