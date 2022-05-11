# 这个程序是为了检查字符训练集中是否有放错位置的图片。原图片高度小，
# 仅有12个像素，不容易看清楚，所以将其放大10倍后放大一起，就便于肉眼检查

from PIL import Image
import os,msvcrt,pyautogui,time

pin = r'./train_imgs/'         # 字符训练集
pout =  r'.\check\\'

iconset = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','m','n','p','r'] #字符集

for letter in iconset:
    w = len (os.listdir (pin + letter))*15
    h = 12
    im = Image.new ('1',(w,h),0)
    num = 0
    x = 0
    for img in os.listdir (pin + letter):
        im0 =Image.open (pin + letter + '/' + img)
        im.paste (im0, (x,0))
        x += im0.size [0]+1
    im = im.crop ((0,0,x,h))
    im = im.resize ((x*10,h*10),Image.ANTIALIAS)
    name = pout + letter.upper()+'.tif'
    im.save(name,dpi=(300.0,300.0))
    os.startfile(name)
    time.sleep(0.2)
    pyautogui.hotkey('alt','tab')
    print("press any key to continue")
    msvcrt.getch()
    
