#!/usr/bin/python3

import argparse
import cv2 as cv
import numpy as np

argparser = argparse.ArgumentParser(description='Remove background from scanned image.')
argparser.add_argument('input',
                       help='Input image')
argparser.add_argument('output',
                       help='Output image')
argparser.add_argument('-k', '--kernel',
                       type=int,
                       default=-1,
                       dest='kernel_size',
                       help='Morphology/blur kernel size to use. By default min(width,height)/10.')
argparser.add_argument('-r', '--resize',
                       type=float,
                       default=2,
                       dest='resize_factor',
                       help='Resize image by factor before applying morphology operations. By default 2')
argparser.add_argument('-m', '--method',
                       type=str,
                       default='morphology',
                       dest='method',
                       help="Method to use. One of 'morphology', 'blur', 'inpaint', or their short hands 'm','b','i'. Default is 'morphology'.")
argparser.add_argument('-b', '--save-background',
                       action='store_true',
                       dest='save_background',
                       help='Save guessed background aswell.')
args = argparser.parse_args()

def get_background_morphology(img, kernel_size, resize_factor):
    old_size = (img.shape[1],img.shape[0])
    if resize_factor != 1.0:
        kernel_size = int(((1 + kernel_size / resize_factor) // 2) * 2 - 1)
        new_size = tuple(round(o/resize_factor) for o in old_size)
        small = cv.resize(img, new_size, interpolation = cv.INTER_AREA)
    else:
        kernel_size = int(kernel_size//2)*2 + 1
        small = img

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel_size, kernel_size))
    bg = cv.morphologyEx(small, cv.MORPH_CLOSE, kernel)

    if resize_factor != 1.0:
        bg = cv.resize(bg, old_size)
    return bg


def get_background_blur(img, kernel_size):
    return cv.blur(img,(kernel_size,kernel_size))

def get_background_infill(img, kernel_size, resize_factor):
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    morph_bg = get_background_morphology(img, kernel_size, resize_factor)
    tmp_nobg = np.uint8(np.clip((gray/cv.cvtColor(morph_bg, cv.COLOR_RGB2GRAY))*255,0,255))
    _,content = cv.threshold(tmp_nobg,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    content = cv.morphologyEx(content,cv.MORPH_ERODE,kernel)
    content = (cv.cvtColor(content, cv.COLOR_GRAY2RGB) == 0)
    # Real Inpainting is rather slow. Instead replacing content pixels with (already calculated) morph_bg
    return np.where(content, morph_bg, img)
    #return cv.inpaint(img, content, 2, cv.INPAINT_TELEA)


img = cv.imread(args.input)

if args.kernel_size < 0:
    args.kernel_size = (min(img.shape[1],img.shape[0])//20)*2+1

if args.method.startswith('b'):
    bg = get_background_blur(img, kernel_size)
elif args.method.startswith('i'):
    bg = get_background_infill(img, args.kernel_size, args.resize_factor)
else:
    bg = get_background_morphology(img, args.kernel_size, args.resize_factor)

img_nobg = (img / bg)*255
cv.imwrite(args.output, img_nobg)
if args.save_background != False:
    if args.save_background == True:
        i = args.output.rfind('.')
        cv.imwrite(f"{args.output[:i]}_bg{args.output[i:]}", bg)
    else:
        cv.imwrite(args.save_background, bg)

