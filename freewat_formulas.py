import math

def lerp(min, max, coeff):
    return (1-coeff)*min + (coeff*max)

def cond(K,L,w,th):
    c = (K*L*w)/th
    return c

