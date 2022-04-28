from PIL import Image
import os
path = os.path.dirname(__file__)
path_in = path + '/3/'
path_out = path + '/4/'

iconset = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','m','n','p','r'] #字符集



for letter in iconset:
    w = len (os.listdir (path_in + letter))*15
    h = 12
    im = Image.new ('1',(w,h),0)
    num = 0
    x = 0
    for img in os.listdir (path_in + letter):
        im0 =Image.open (path_in + letter + '/' + img)
        im.paste (im0, (x,0))
        x += im0.size [0]+1
    im = im.crop ((0,0,x,h))
    im = im.resize ((x*10,h*10),Image.ANTIALIAS)
    im.save(path_out + letter.upper()+'.tif',dpi=(300.0,300.0))
