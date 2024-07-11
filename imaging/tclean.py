#!/usr/bin/env python

import os
import numpy as np
import glob
import time
import shutil
import argparse
from casatasks import tclean, exportfits, casalog
logfile = casalog.logfile()

from astropy.io import fits


if __name__ == '__main__':

    description = "Image each selected channel, reading from the split out MS. "\
    "Since this script is run independently of the split script, the same split "\
    "parameters need to be passed in to reconstruct the output image file name"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input_MS', type=str, help='File to split')
    parser.add_argument('--channel_number', type=int, help='Channel number to split')
    parser.add_argument('--nchannels', type=int, default=1, help='Number of channels to split')
    parser.add_argument('--spw', type=int, default=0, help='SPW from which to split the channels')
    parser.add_argument('--gridder', type=str, default='standard', help='Gridder to use')
    parser.add_argument('--imsize', type=int, default=128, help='Image size in pixels')
    parser.add_argument('--cell', type=str, default='0.004arcsec', help='Cell size')
    parser.add_argument('--stokes', type=str, default='I', help='Stokes parameters to image')
    parser.add_argument('--niter', type=int, default=0, help='Number of iterations')
    parser.add_argument('--usemask', type=str, default='user', help='Masking mode')
    parser.add_argument('--threshold', type=str, default='0.0mJy', help='Threshold for cleaning')
    args = parser.parse_args()

    casalog.setlogfile('logs/{SLURM_JOB_NAME}_{SLURM_ARRAY_JOB_ID}_{SLURM_ARRAY_TASK_ID}.casa'.format(**os.environ))

    msname = args.input_MS
    # Assume SLURM_ARRAY_JOB_ID is passed in as --channel-number
    outputvis = os.path.basename(msname).replace('.ms', f'_spw_{args.spw:02d}_channel_{args.channel_number:04d}.ms')
    imagename = outputvis.strip('.ms')

    chan = args.channel_number
    chan_beg = 8*chan
    chan_end = 8*(chan+1) - 1

    retdict = tclean(vis=msname, imagename=imagename, imsize=args.imsize, cell=args.cell, specmode='mfs',
           selectdata=True, spw=f"{args.spw}:{chan_beg}~{chan_end}", usemask=args.usemask,
           stokes=args.stokes,gridder=args.gridder, niter=args.niter, threshold=args.threshold, parallel=False,
	   fullsummary=True)

    np.save(imagename + '_retdict.npy', retdict)

    exportfits(imagename=imagename+'.image', fitsimage=imagename+'.fits', overwrite=True)
    # Zip up the cube to save space - astropy.fits should be able to handle gz FITS for concat
    #os.system(f'gzip {imagename}.fits\n')

    # Clean up the intermediate files
    exts = ['.psf', '.residual', '.sumwt', '.weight', '.pb', '.image', '.model', '.ms', '.mask']
    for ext in exts:
        imname = imagename + ext
        if os.path.exists(imname):
            shutil.rmtree(imname)

    #if os.path.exists(imagename+'.fits'):
    #    os.remove(imagename+'.fits')

