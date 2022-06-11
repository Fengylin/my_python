import pyautogui
import time
import os
from PIL import Image,ImageDraw

def ez_map(thresold):
    res=[]
    for i in range(256):
        if i<thresold: res.append(1)
        else: res.append(0)    
    return res 


#图片转化为灰度图片并二值化
def pre_hd_ez(img):
    img=img.convert("L")   
    thresold=100
    table=ez_map(thresold)
    img=img.point(table,'1')
    return img

def find_letters(im2):                               # 形成单字符图像分割线
    inletter = False
    foundletter=False
    start = 0
    end = 0
    letters = [] #待识别的字符
    for y in range(im2.size[0]): # slice across，
        for x in range(im2.size[1]): # slice down
            pix = im2.getpixel((y,x))
            if pix != 0: inletter = True                

        if foundletter == False and inletter == True:
            foundletter = True
            start = y

        if foundletter == True and inletter == False:
            foundletter = False
            end = y-1
            letters.append((start,end)) 

        inletter=False
    if start > end : letters.append ((start,y))
    return letters


def black_points (im):                                # 统计图像中的黑点坐标
    dict = {}
    im = im.convert ('1')
    for x in range(im.size[0]): 
        for y in range(im.size[1]):
            pix = im.getpixel((x,y))
            if pix !=0: dict [(x,y)] = 0
    return dict

def find(xy,wh, letters,num,sub=[]):
    x,y = xy[0],xy[1]
    w,h = wh[0],wh[1]
    if xy not in letters:return
    if letters[xy] == num:return
    else:
        sub.append(xy)
        letters[xy] = num

    if x+1 <  w: find((x+1,y),wh,letters,num,sub)
    if x-1 > -1: find((x-1,y),wh,letters,num,sub)
    if y-1 > -1: find((x,y-1),wh,letters,num,sub)
    if y+1 <  h: find((x,y+1),wh,letters,num,sub)

def denoise(img):
    blp = black_points (img)
    num = 1
    all_str = []            # 全部子串
    w,h =img.size
    for point in blp:
        sub_str =[]
        if blp [point] != 0:
            continue
        find(point,img.size,blp,num,sub_str)
        all_str.append(sub_str)
        num += 1
    all_str.sort(key=len)
    print ("子串数目：{:4}".format(len(all_str)))
    for sub_str in all_str:
        if len(sub_str) >8 :continue
        for point in sub_str: img.putpixel(point,0)
    return

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    path_in=path + "/origin_imgs/"      # 原始图片目录
    path_out=path +'/contrast_imgs/'    # 前后比较图片目录
    path_idt=path +'/WB_imgs/'          # 处理完成后的黑白图片目录
    im=Image.open(path_in+'1.png')      # 任取一张典型图片，获取图片尺寸
    repeat = 1                          # 降噪迭代次数
    w,h = im.size
    im_new=Image.new('RGB', (w, h*3+10), (255, 255, 255)) #对比图片
    im.close()
    no_tif =0
    im_fill = Image.new ('1',(1,h),0)
    in_fill = Image.new ('1',(1,w),0)
    for image in os.listdir(path_in):
        tif =  "{:0>3d}{}".format(no_tif,'.tif')     # 输出图片统一编号
        print ('\n',tif,image,end='  ')
        if not os.path.isfile(path_in+image):
            continue
        img=Image.open(path_in+image)
        im_new.paste(img,(0,0))             # 原始图像
        #img = noise_clean(img,1,9,12)       # 降噪
        img=pre_hd_ez(img) 
        im_new.paste(img,(0,h+5))
        denoise (img)                 # 遍历降噪
        im_new.paste(img,(0,2*h+10))
        im_new.save(path_out+tif)           # 生成比较图像
        img.save(path_idt+tif,dpi=(300.0,300.0)) #处理完成的图片
        no_tif += 1

        letters = find_letters(img)         # 字符分割线
        
        hl, hr = 9,21                       # hl,有效字符上部空白，hr-hl:字符有效高度
        num = 1
        for xl, xr in letters:
            im = img.crop ((xl,hl,xr+1,hr))
            im.save (path + '/letters_imgs/'+str(num)+tif,dpi=(300.0,300.0)) # 单字符图片
            num += 1
