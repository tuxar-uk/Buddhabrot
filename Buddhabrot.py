'''
    Buddhabrot.py     Copyright (C) 2015 Alan Richmond (Tuxar.uk, FractalArt.Gallery)
    =============     MIT License
'''
import pygame,os,sys
import random as r
from collections import deque
from math import sqrt,log

side=height=2**10               # must be power of 2
width=int(1.5*side)             # going to be 3*2 squares
maxit=2**11;minit=2**5          # max & min iterations
grey=True                       # colour or greyscale?
logf=False                      # log or sqrt intensity distribution
sqrtf=True
discf=32                        # discard this proportion of lower values
mulf=1.1                        # multiply intensity by this

#   Encode parameters into filename
dir="/home/alan/Pictures/Buddhabrots/BB-{0}-{1}-{2}_{3}x{4}/".format(discf,minit,maxit,width,height)
print dir
if os.path.exists(dir):
    ok=raw_input("Directory exists. OK to write in it (N/y)?")
    if ok != 'y': sys.exit()
else:
    os.makedirs(dir)

#   Complex plane
whr=float(width)/float(height)
xmin,xmax = -2.0, 1.0
xd = xmax - xmin
ymax = xd/(whr*2)
ymin = -ymax
yd = ymax - ymin
xscale = xd / float(width)
yscale = yd / float(height)

maxp=0
pixel=[[0 for iy in range(height)] for ix in range(width)]

#   Increments each pixel's count where the orbit passes through
def Buddha(orbit):
    global maxp
    for z in orbit:     # for each point z in orbit:
        x=z.real
        y=z.imag
        ix=int((x-xmin)/xscale+0.5)         # map to display position
        iy=int((y-ymax)/(-yscale)+0.5)
        if ix>=0 and ix<width and iy>=0 and iy<height:
            if iy<=height/2:
                pixel[ix][iy]+=1
                p=pixel[ix][iy]
            else:
                pixel[ix][height-iy]+=1
                p=pixel[ix][height-iy]
            if p>maxp:
                maxp=p

xs2=xscale/2.0
ys2=yscale/2.0
zpoints=[]
already = [[-1 for y in range(side/2)] for x in range(side*3/2)]
#   Test if point z=(x,y) is in Mandelbrot set
def mandel(ix, iy):
    global already
    if not budit:
        it = already[ix][iy]    # has this point already been seen?
        if (it > -1): return it

    x=xscale * ix + xmin;y=-yscale * iy + ymax
    if budit:
        x+=r.uniform(-xs2,xs2)
        y+=r.uniform(-ys2,ys2)
#   Optimisation: check if not in cardioid or main circle
    y2=y*y
    q=(x-0.25)**2+y2
    if not(q*(q+(x-0.25))<y2/4.0 or (x+1.0)**2 + y2 <0.0625):
        c=complex(x,y)      # call this point 'c'
        z=complex(0,0)      # start iteration from 0
        orbit=[]
        for it in xrange(maxit):    # iterate up to maximum
            z*=z
            z+=c
            if budit:   orbit.append(z) # add this point to orbit
            if abs(z)>2:                # escaped from set?
                if budit:   Buddha(orbit)   # add to density count
                else:                       # add to list of points to use later
                    if it>minit:  zpoints.append((ix,iy))
                break
        else:   it=maxit
    else:   it=maxit+1
    if not budit:    already[ix][iy] = it
#   in set
    return it

fg = pygame.Color(0, 0, 0, 0)
d = pygame.display.set_mode((width,height))

def Pixel(ix,iy):
    global fg

    iz=pixel[ix][iy]
    jj=maxp/discf        # discf>0!
    if iz>jj:
        if logf:     f=log(float(iz-jj),10)/log(float(maxp-jj),10)
        elif sqrtf:  f=sqrt(float(iz-jj))/sqrt(float(maxp-jj))
        else:       f=float(iz-jj)/float(maxp-jj)
        f*=mulf
        if grey:
            c=f*255
            if c>255: c=255
            fg=(c,c,c)
        else:
            h=f
            v=s=1
            fg=(h,s,v)
        d.set_at((ix,iy),fg)
        d.set_at((ix,height-iy-1),fg)

def Display():
    d.fill((0,0,0))
    for ix in xrange(width):
        for iy in xrange(height/2):
            Pixel(ix,iy)
    pygame.display.flip()

budit=False

def QuadTree():
    global budit, savit
#   Add 3 squares to queue, in a line on top of the real axis
    squares = deque([(0, 0, side / 2), (side / 2, 0, side / 2), (side,0,side/2)])
#   Pop squares off the queue
    while squares:
        ix, iy, l = squares.popleft()
        l2 = l / 2
#       Determine colour
        if l == 1:      # down to 1 pixel

            mandel(ix,iy)
            di=0

        else:
#           Get iteration counts at 4 corners.
            it = [mandel(ix, iy),
                  mandel(ix + l - 1, iy),
                  mandel(ix + l - 1, iy + l - 1),
                  mandel(ix, iy + l - 1)]
            di = max(it) - min(it)

#       Subdivide square; midpoints
        ixn = ix + l2
        iyn = iy + l2

#       If squares are more than 1 pixel, and there's a variation of iteration counts
        if l > 1 and di > 0:
#           Add sub-squares to queue
            squares.append((ix, iy, l2))
            squares.append((ixn, iy, l2))
            squares.append((ixn, iyn, l2))
            squares.append((ix, iyn, l2))

budit=False
QuadTree()
budit=True
nrand=0
while True:
    for p in zpoints:
        (ix,iy)=p
        mandel(ix,iy)

    Display()
    nrand+=1
    print nrand,
    file=dir+str(nrand)+'.jpg'
    pygame.image.save(d, file)