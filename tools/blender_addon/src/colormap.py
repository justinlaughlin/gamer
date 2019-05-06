# ***************************************************************************
# This file is part of the GAMer software.
# Copyright (C) 2016-2018
# by Christopher Lee, Tom Bartol, John Moody, Rommie Amaro, J. Andrew McCammon,
#    and Michael Holst

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# ***************************************************************************


import numpy as np

def getColor(data, colormapKey, minV=-1000, maxV=1000, percentTruncate=False):
    colorStyle = colormapDict[colormapKey]

    print("*** Pre Truncation ***")
    print("Minimum value: %s; Maximum value: %s"%(np.amin(data),np.amax(data)))
    print("Mean value: %s; Median value: %s"%(np.mean(data),np.median(data)))
    
    # the minV/maxV values are percentiles instead
    if percentTruncate:
        print("Using min/max values as percentiles!")
        if minV < 0 or minV >= 100:
            print("Minimum percentile must be 0<=x<100. Setting to 0")
            lowerPercentile = 0
        else:
            lowerPercentile = int(minV)
        if maxV <= 0 or maxV > 100:
            print("Maximum percentile must be 0<x<=1. Setting to 100")
            upperPercentile = 100
        else:
            upperPercentile = int(maxV)

        minV = np.percentile(data,lowerPercentile)
        maxV = np.percentile(data,upperPercentile)
        print("Data truncated at %f and %f percentiles"%(lowerPercentile,upperPercentile) )       
        # if colormapKey == 'gauss':
        #     absV = np.max((np.abs(minV),np.abs(maxV)))
        #     minV, maxV = (-absV, absV)
        #     print("Data symmetrized around 0")
    
    # Truncate at min and max
    data[data < minV] = minV
    data[data > maxV] = maxV
    #amin = np.amin(data)

    print("*** Post Truncation***")
    print("Minimum value: %s; Maximum value: %s"%(np.amin(data),np.amax(data)))
    print("Mean value: %s; Median value: %s"%(np.mean(data),np.median(data)))

    # Normalize based on minV and maxV so colorbar is scaled accordingly
    data = data - minV # set values at minV to 0
    data = data/(maxV-minV) # set values which were at maxV to 1
    
    print('normalized data min/max: %f' % np.amin(data))
    print('normalized data max: %f' % np.amax(data))
    chunk = 1/(len(colorStyle)-2)
    remainder = np.mod(data, chunk)
    idx = np.floor_divide(data, chunk).astype(int)
    colors = colorStyle[idx]*(1-remainder)[:,None] + colorStyle[idx+1]*(remainder)[:,None]
    #print('min/max color index: %d, %d' % (np.amin(idx), np.amax(idx)))

    # this depends on matplotlib
    #if plotColorBar:
    #    genColorBar(colorStyle,minV,maxV)

    return colors

def genColorBar(colorStyle,minV,maxV,fontsize,orientation='vertical'):
    """
    Generates a figure of a colormap
    colorStyle: either numpy array or palettable colormap
    """
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    fig = plt.figure(figsize=(3,8))
    if orientation=='horizontal':
        ax = fig.add_axes([0.05,0.80,0.9,0.15])
    elif orientation=='vertical':
        ax = fig.add_axes([0.05,0.05,0.15,0.9])
    if type(colorStyle) == np.ndarray:
        cmap = mpl.colors.LinearSegmentedColormap.from_list('name',colorStyle)
    else:
        cmap = colorStyle.mpl_colormap
    #cmap = colorStyle.mpl_colormap
    # cmap = mpl.colors.LinearSegmentedColormap.from_list('name',colorStyle) # if input is a numpy array
    cnorm = mpl.colors.Normalize(vmin=minV,vmax=maxV)
    cb = mpl.colorbar.ColorbarBase(ax,cmap=cmap,norm=cnorm,orientation=orientation,format=ticker.FuncFormatter(eng_notation))
    cb.ax.tick_params(labelsize=fontsize)
    #ax.ticklabel_format(axis='both',style='sci')
    fig.show()

def eng_notation(x,pos):
    num, power = '{:.1e}'.format(x).split('e')
    power=int(power)
    return r'${} \times 10^{{{}}}$'.format(num,power)

# Example of importing a colormap from palettable:
# import numpy as np
# from palettable.colorbrewer.diverging import RdBu_7_r
# import matplotlib as mpl
# np.array(RdBu_7_r.mpl_colors)

colormapDict = {"BuRd": np.array([[0.12941176, 0.4       , 0.6745098 ],
       [0.40392157, 0.6627451 , 0.81176471],
       [0.81960784, 0.89803922, 0.94117647],
       [0.96862745, 0.96862745, 0.96862745],
       [0.99215686, 0.85882353, 0.78039216],
       [0.9372549 , 0.54117647, 0.38431373],
       [0.69803922, 0.09411765, 0.16862745]]),
      "BrBG_11": np.array([[0.32941176, 0.18823529, 0.01960784],
       [0.54901961, 0.31764706, 0.03921569],
       [0.74901961, 0.50588235, 0.17647059],
       [0.8745098 , 0.76078431, 0.49019608],
       [0.96470588, 0.90980392, 0.76470588],
       [0.96078431, 0.96078431, 0.96078431],
       [0.78039216, 0.91764706, 0.89803922],
       [0.50196078, 0.80392157, 0.75686275],
       [0.20784314, 0.59215686, 0.56078431],
       [0.00392157, 0.4       , 0.36862745],
       [0.        , 0.23529412, 0.18823529]]),
       "Oranges_8": np.array([[1.        , 0.96078431, 0.92156863],
       [0.99607843, 0.90196078, 0.80784314],
       [0.99215686, 0.81568627, 0.63529412],
       [0.99215686, 0.68235294, 0.41960784],
       [0.99215686, 0.55294118, 0.23529412],
       [0.94509804, 0.41176471, 0.0745098 ],
       [0.85098039, 0.28235294, 0.00392157],
       [0.54901961, 0.17647059, 0.01568627]]),
       "bgr": np.array([[0,0,255],
       [0,27,235],
       [0,54,215],
       [0,81,195],
       [0,108,174],
       [0,135,151],
       [0,162,117],
       [0,189,84],
       [0,216,50],
       [0,242,17],
       [17,242,0],
       [50,216,0],
       [83,189,0],
       [116,162,0],
       [149,135,0],
       [172,108,0],
       [193,81,0],
       [214,54,0],
       [235,27,0],
       [255,0,0]])/255}

# BuRd = np.array([[0.12941176, 0.4       , 0.6745098 ],
#        [0.40392157, 0.6627451 , 0.81176471],
#        [0.81960784, 0.89803922, 0.94117647],
#        [0.96862745, 0.96862745, 0.96862745],
#        [0.99215686, 0.85882353, 0.78039216],
#        [0.9372549 , 0.54117647, 0.38431373],
#        [0.69803922, 0.09411765, 0.16862745]])

# BrBG_11 = np.array([[0.32941176, 0.18823529, 0.01960784],
#        [0.54901961, 0.31764706, 0.03921569],
#        [0.74901961, 0.50588235, 0.17647059],
#        [0.8745098 , 0.76078431, 0.49019608],
#        [0.96470588, 0.90980392, 0.76470588],
#        [0.96078431, 0.96078431, 0.96078431],
#        [0.78039216, 0.91764706, 0.89803922],
#        [0.50196078, 0.80392157, 0.75686275],
#        [0.20784314, 0.59215686, 0.56078431],
#        [0.00392157, 0.4       , 0.36862745],
#        [0.        , 0.23529412, 0.18823529]])

# Oranges_8 = np.array([[1.        , 0.96078431, 0.92156863],
#        [0.99607843, 0.90196078, 0.80784314],
#        [0.99215686, 0.81568627, 0.63529412],
#        [0.99215686, 0.68235294, 0.41960784],
#        [0.99215686, 0.55294118, 0.23529412],
#        [0.94509804, 0.41176471, 0.0745098 ],
#        [0.85098039, 0.28235294, 0.00392157],
#        [0.54901961, 0.17647059, 0.01568627]])

# #https://jdherman.github.io/colormap/
# # blue green red
# bgr=np.array([[0,0,255],
# [0,27,235],
# [0,54,215],
# [0,81,195],
# [0,108,174],
# [0,135,151],
# [0,162,117],
# [0,189,84],
# [0,216,50],
# [0,242,17],
# [17,242,0],
# [50,216,0],
# [83,189,0],
# [116,162,0],
# [149,135,0],
# [172,108,0],
# [193,81,0],
# [214,54,0],
# [235,27,0],
# [255,0,0]])/255




viridis = np.array([[0.26666667, 0.00392157, 0.32941176],
       [0.26666667, 0.00784314, 0.3372549 ],
       [0.27058824, 0.01568627, 0.34117647],
       [0.27058824, 0.01960784, 0.34901961],
       [0.2745098 , 0.02745098, 0.35294118],
       [0.2745098 , 0.03137255, 0.36078431],
       [0.2745098 , 0.03921569, 0.36470588],
       [0.2745098 , 0.04313725, 0.36862745],
       [0.27843137, 0.05098039, 0.37647059],
       [0.27843137, 0.05490196, 0.38039216],
       [0.27843137, 0.0627451 , 0.38823529],
       [0.27843137, 0.06666667, 0.39215686],
       [0.27843137, 0.0745098 , 0.39607843],
       [0.28235294, 0.07843137, 0.40392157],
       [0.28235294, 0.08627451, 0.40784314],
       [0.28235294, 0.09019608, 0.41176471],
       [0.28235294, 0.09411765, 0.41568627],
       [0.28235294, 0.10196078, 0.42352941],
       [0.28235294, 0.10588235, 0.42745098],
       [0.28235294, 0.10980392, 0.43137255],
       [0.28235294, 0.11372549, 0.43529412],
       [0.28235294, 0.12156863, 0.43921569],
       [0.28235294, 0.1254902 , 0.44313725],
       [0.28235294, 0.12941176, 0.45098039],
       [0.28235294, 0.1372549 , 0.45490196],
       [0.28235294, 0.14117647, 0.45882353],
       [0.28235294, 0.14509804, 0.4627451 ],
       [0.28235294, 0.14901961, 0.46666667],
       [0.28235294, 0.15686275, 0.47058824],
       [0.28235294, 0.16078431, 0.4745098 ],
       [0.27843137, 0.16470588, 0.47843137],
       [0.27843137, 0.17254902, 0.47843137],
       [0.27843137, 0.17647059, 0.48235294],
       [0.27843137, 0.18039216, 0.48627451],
       [0.27843137, 0.18431373, 0.49019608],
       [0.2745098 , 0.18823529, 0.49411765],
       [0.2745098 , 0.19607843, 0.49411765],
       [0.2745098 , 0.2       , 0.49803922],
       [0.2745098 , 0.20392157, 0.50196078],
       [0.27058824, 0.20784314, 0.50588235],
       [0.27058824, 0.21568627, 0.50588235],
       [0.27058824, 0.21960784, 0.50980392],
       [0.26666667, 0.22352941, 0.51372549],
       [0.26666667, 0.22745098, 0.51372549],
       [0.26666667, 0.23137255, 0.51764706],
       [0.2627451 , 0.23921569, 0.51764706],
       [0.2627451 , 0.24313725, 0.52156863],
       [0.25882353, 0.24705882, 0.52156863],
       [0.25882353, 0.25098039, 0.5254902 ],
       [0.25882353, 0.25490196, 0.5254902 ],
       [0.25490196, 0.25882353, 0.52941176],
       [0.25490196, 0.26666667, 0.52941176],
       [0.25098039, 0.27058824, 0.53333333],
       [0.25098039, 0.2745098 , 0.53333333],
       [0.24705882, 0.27843137, 0.53333333],
       [0.24705882, 0.28235294, 0.5372549 ],
       [0.24313725, 0.28627451, 0.5372549 ],
       [0.24313725, 0.29019608, 0.5372549 ],
       [0.24313725, 0.29803922, 0.54117647],
       [0.23921569, 0.30196078, 0.54117647],
       [0.23921569, 0.30588235, 0.54117647],
       [0.23529412, 0.30980392, 0.54117647],
       [0.23529412, 0.31372549, 0.54509804],
       [0.23137255, 0.31764706, 0.54509804],
       [0.23137255, 0.32156863, 0.54509804],
       [0.22745098, 0.3254902 , 0.54509804],
       [0.22745098, 0.32941176, 0.54901961],
       [0.22352941, 0.33333333, 0.54901961],
       [0.22352941, 0.3372549 , 0.54901961],
       [0.21960784, 0.34509804, 0.54901961],
       [0.21960784, 0.34901961, 0.54901961],
       [0.21568627, 0.35294118, 0.54901961],
       [0.21568627, 0.35686275, 0.55294118],
       [0.21176471, 0.36078431, 0.55294118],
       [0.21176471, 0.36470588, 0.55294118],
       [0.20784314, 0.36862745, 0.55294118],
       [0.20784314, 0.37254902, 0.55294118],
       [0.20392157, 0.37647059, 0.55294118],
       [0.20392157, 0.38039216, 0.55294118],
       [0.2       , 0.38431373, 0.55294118],
       [0.2       , 0.38823529, 0.55294118],
       [0.19607843, 0.39215686, 0.55686275],
       [0.19607843, 0.39607843, 0.55686275],
       [0.19215686, 0.4       , 0.55686275],
       [0.19215686, 0.40392157, 0.55686275],
       [0.19215686, 0.40784314, 0.55686275],
       [0.18823529, 0.41176471, 0.55686275],
       [0.18823529, 0.41568627, 0.55686275],
       [0.18431373, 0.41960784, 0.55686275],
       [0.18431373, 0.42352941, 0.55686275],
       [0.18039216, 0.42745098, 0.55686275],
       [0.18039216, 0.43137255, 0.55686275],
       [0.18039216, 0.43529412, 0.55686275],
       [0.17647059, 0.43921569, 0.55686275],
       [0.17647059, 0.44313725, 0.55686275],
       [0.17254902, 0.44313725, 0.55686275],
       [0.17254902, 0.44705882, 0.55686275],
       [0.17254902, 0.45098039, 0.55686275],
       [0.16862745, 0.45490196, 0.55686275],
       [0.16862745, 0.45882353, 0.55686275],
       [0.16470588, 0.4627451 , 0.55686275],
       [0.16470588, 0.46666667, 0.55686275],
       [0.16470588, 0.47058824, 0.55686275],
       [0.16078431, 0.4745098 , 0.55686275],
       [0.16078431, 0.47843137, 0.55686275],
       [0.16078431, 0.48235294, 0.55686275],
       [0.15686275, 0.48627451, 0.55686275],
       [0.15686275, 0.49019608, 0.55686275],
       [0.15294118, 0.49411765, 0.55686275],
       [0.15294118, 0.49803922, 0.55686275],
       [0.15294118, 0.50196078, 0.55686275],
       [0.14901961, 0.50588235, 0.55686275],
       [0.14901961, 0.50980392, 0.55686275],
       [0.14901961, 0.50980392, 0.55686275],
       [0.14509804, 0.51372549, 0.55686275],
       [0.14509804, 0.51764706, 0.55686275],
       [0.14509804, 0.52156863, 0.55686275],
       [0.14117647, 0.5254902 , 0.55686275],
       [0.14117647, 0.52941176, 0.55686275],
       [0.1372549 , 0.53333333, 0.55686275],
       [0.1372549 , 0.5372549 , 0.55686275],
       [0.1372549 , 0.54117647, 0.55294118],
       [0.13333333, 0.54509804, 0.55294118],
       [0.13333333, 0.54901961, 0.55294118],
       [0.13333333, 0.55294118, 0.55294118],
       [0.12941176, 0.55686275, 0.55294118],
       [0.12941176, 0.56078431, 0.55294118],
       [0.12941176, 0.56470588, 0.55294118],
       [0.12941176, 0.56862745, 0.54901961],
       [0.1254902 , 0.57254902, 0.54901961],
       [0.1254902 , 0.57254902, 0.54901961],
       [0.1254902 , 0.57647059, 0.54901961],
       [0.12156863, 0.58039216, 0.54901961],
       [0.12156863, 0.58431373, 0.54509804],
       [0.12156863, 0.58823529, 0.54509804],
       [0.12156863, 0.59215686, 0.54509804],
       [0.12156863, 0.59607843, 0.54509804],
       [0.12156863, 0.6       , 0.54117647],
       [0.12156863, 0.60392157, 0.54117647],
       [0.11764706, 0.60784314, 0.54117647],
       [0.11764706, 0.61176471, 0.5372549 ],
       [0.11764706, 0.61568627, 0.5372549 ],
       [0.12156863, 0.61960784, 0.5372549 ],
       [0.12156863, 0.62352941, 0.53333333],
       [0.12156863, 0.62745098, 0.53333333],
       [0.12156863, 0.63137255, 0.53333333],
       [0.12156863, 0.63137255, 0.52941176],
       [0.12156863, 0.63529412, 0.52941176],
       [0.1254902 , 0.63921569, 0.5254902 ],
       [0.1254902 , 0.64313725, 0.5254902 ],
       [0.12941176, 0.64705882, 0.52156863],
       [0.12941176, 0.65098039, 0.52156863],
       [0.13333333, 0.65490196, 0.52156863],
       [0.13333333, 0.65882353, 0.51764706],
       [0.1372549 , 0.6627451 , 0.51372549],
       [0.14117647, 0.66666667, 0.51372549],
       [0.14509804, 0.67058824, 0.50980392],
       [0.14509804, 0.6745098 , 0.50980392],
       [0.14901961, 0.67843137, 0.50588235],
       [0.15294118, 0.67843137, 0.50588235],
       [0.15686275, 0.68235294, 0.50196078],
       [0.16078431, 0.68627451, 0.49803922],
       [0.16470588, 0.69019608, 0.49803922],
       [0.17254902, 0.69411765, 0.49411765],
       [0.17647059, 0.69803922, 0.49019608],
       [0.18039216, 0.70196078, 0.48627451],
       [0.18431373, 0.70588235, 0.48627451],
       [0.19215686, 0.70980392, 0.48235294],
       [0.19607843, 0.71372549, 0.47843137],
       [0.20392157, 0.71372549, 0.4745098 ],
       [0.20784314, 0.71764706, 0.4745098 ],
       [0.21568627, 0.72156863, 0.47058824],
       [0.21960784, 0.7254902 , 0.46666667],
       [0.22745098, 0.72941176, 0.4627451 ],
       [0.23137255, 0.73333333, 0.45882353],
       [0.23921569, 0.7372549 , 0.45490196],
       [0.24705882, 0.7372549 , 0.45098039],
       [0.25098039, 0.74117647, 0.44705882],
       [0.25882353, 0.74509804, 0.44313725],
       [0.26666667, 0.74901961, 0.43921569],
       [0.2745098 , 0.75294118, 0.43529412],
       [0.28235294, 0.75686275, 0.43137255],
       [0.29019608, 0.75686275, 0.42745098],
       [0.29803922, 0.76078431, 0.42352941],
       [0.30588235, 0.76470588, 0.41960784],
       [0.31372549, 0.76862745, 0.41568627],
       [0.32156863, 0.77254902, 0.41176471],
       [0.32941176, 0.77254902, 0.40784314],
       [0.3372549 , 0.77647059, 0.40392157],
       [0.34509804, 0.78039216, 0.39607843],
       [0.35294118, 0.78431373, 0.39215686],
       [0.36078431, 0.78431373, 0.38823529],
       [0.36862745, 0.78823529, 0.38431373],
       [0.37647059, 0.79215686, 0.37647059],
       [0.38823529, 0.79607843, 0.37254902],
       [0.39607843, 0.79607843, 0.36862745],
       [0.40392157, 0.8       , 0.36078431],
       [0.41176471, 0.80392157, 0.35686275],
       [0.42352941, 0.80392157, 0.35294118],
       [0.43137255, 0.80784314, 0.34509804],
       [0.43921569, 0.81176471, 0.34117647],
       [0.45098039, 0.81568627, 0.3372549 ],
       [0.45882353, 0.81568627, 0.32941176],
       [0.46666667, 0.81960784, 0.3254902 ],
       [0.47843137, 0.81960784, 0.31764706],
       [0.48627451, 0.82352941, 0.31372549],
       [0.49803922, 0.82745098, 0.30588235],
       [0.50588235, 0.82745098, 0.30196078],
       [0.51764706, 0.83137255, 0.29411765],
       [0.5254902 , 0.83529412, 0.28627451],
       [0.5372549 , 0.83529412, 0.28235294],
       [0.54509804, 0.83921569, 0.2745098 ],
       [0.55686275, 0.83921569, 0.27058824],
       [0.56470588, 0.84313725, 0.2627451 ],
       [0.57647059, 0.84313725, 0.25490196],
       [0.58431373, 0.84705882, 0.25098039],
       [0.59607843, 0.84705882, 0.24313725],
       [0.60784314, 0.85098039, 0.23529412],
       [0.61568627, 0.85098039, 0.23137255],
       [0.62745098, 0.85490196, 0.22352941],
       [0.63529412, 0.85490196, 0.21568627],
       [0.64705882, 0.85882353, 0.21176471],
       [0.65882353, 0.85882353, 0.20392157],
       [0.66666667, 0.8627451 , 0.19607843],
       [0.67843137, 0.8627451 , 0.18823529],
       [0.69019608, 0.86666667, 0.18431373],
       [0.69803922, 0.86666667, 0.17647059],
       [0.70980392, 0.87058824, 0.16862745],
       [0.72156863, 0.87058824, 0.16078431],
       [0.72941176, 0.87058824, 0.15686275],
       [0.74117647, 0.8745098 , 0.14901961],
       [0.75294118, 0.8745098 , 0.14509804],
       [0.76078431, 0.8745098 , 0.1372549 ],
       [0.77254902, 0.87843137, 0.12941176],
       [0.78431373, 0.87843137, 0.1254902 ],
       [0.79215686, 0.88235294, 0.12156863],
       [0.80392157, 0.88235294, 0.11372549],
       [0.81568627, 0.88235294, 0.10980392],
       [0.82352941, 0.88627451, 0.10588235],
       [0.83529412, 0.88627451, 0.10196078],
       [0.84705882, 0.88627451, 0.09803922],
       [0.85490196, 0.89019608, 0.09803922],
       [0.86666667, 0.89019608, 0.09411765],
       [0.8745098 , 0.89019608, 0.09411765],
       [0.88627451, 0.89411765, 0.09411765],
       [0.89803922, 0.89411765, 0.09803922],
       [0.90588235, 0.89411765, 0.09803922],
       [0.91764706, 0.89803922, 0.10196078],
       [0.9254902 , 0.89803922, 0.10588235],
       [0.9372549 , 0.89803922, 0.10980392],
       [0.94509804, 0.89803922, 0.11372549],
       [0.95686275, 0.90196078, 0.11764706],
       [0.96470588, 0.90196078, 0.1254902 ],
       [0.97254902, 0.90196078, 0.12941176],
       [0.98431373, 0.90588235, 0.1372549 ],
       [0.99215686, 0.90588235, 0.14509804]])