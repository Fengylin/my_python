import pyautogui
import time
import xlrd
import pyperclip
import webbrowser
import os
from PIL import Image,ImageDraw

def ez_map(thresold):
    res=[]
    for i in range(256):
        if i<thresold:
            res.append(1)
        else:
            res.append(0)    
    return res 


#图片转化为灰度图片并二值化
def pre_hd_ez(img):
    img=img.convert("L")   
    thresold=100
    table=ez_map(thresold)
    img=img.point(table,'1')
    return img

################################################
#8邻降噪,layer=1.                              #
#return 0,表示该点黑                           #
#return 1,表示该点白                           #
################################################

def get_jz_color(img,x,y,level,layer): 
    color_now=img.getpixel((x,y))
    zero=0
    one=0
    all_point=0
    threshold,k=6,2
    if level >1 :
        threshold,k = 5, 3
    for i in range(0-layer,0+layer+1):
        if x-i<0 or x+i>=img.size[0]:
            continue

        for j in range(0-layer,0+layer+1):
            if y-j<0 or y+j>=img.size[1]:
                continue
            if i==0 and j==0:
                continue
            if img.getpixel((x+i,y+j))==0:
                zero+=1
            else:
                one+=1
            all_point+=1
    if color_now==1:
        l,m = 0,0
        if level > 0: #单像素端头
            for i in  range(-1,2):
                if x-i<0 or y-i<0 or x+i>=img.size[0] or y+i>=img.size[1]:
                    continue
                if img.getpixel((x+i,y))==1:
                    l += 1
                if img.getpixel((x,y+i))==1:
                    m += 1
        if zero/all_point>threshold/8 and l<k and m<k:
            return 0
        else:
            return 1
    if color_now==0:              
        if one/all_point>7/8:
            return 1
        else:
            return 0

def pre_jz(img,level):
    img_after_table=[]
    if level >1: #深度降噪
        for x in range(img.size[0]):
            img_after_table.append([])
            for y in range(img.size[1]):
                color_now=img.getpixel((x,y))
                if  color_now ==0:
                    img_after_table[x].append(0)
                    continue
                num_color=get_jz_color(img,x,y,level,1) #8邻
                img_after_table[x].append(num_color)
        draw = ImageDraw.Draw(img)
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                draw.point((i,j),img_after_table[i][j])
        return img
# 前两次降噪    

    for x in range(img.size[0]):
        img_after_table.append([])
        for y in range(img.size[1]):
            num_color=get_jz_color(img,x,y,level,1)         #8邻
            img_after_table[x].append(num_color)
    draw = ImageDraw.Draw(img)
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            draw.point((i,j),img_after_table[i][j])

    return img

def noise_clean(img,rp,h0,height):
#------------------------------------------------------------------#
# 去噪                                                             #
# 1，转为灰度图像                                                  #
# 2，二值化                                                        #
# 3，八邻降噪                                                      #
# 4，字符之间降噪                                                  #
# 5，字符高度固定，高度空间之外降噪                                #
# 参数：img为打开的图像，rp:八邻次数，h0：字符起始位置             #
#       height:字符高度                                            #
#------------------------------------------------------------------#

    w,h = img.size 
    im2 = Image.new('RGB', (w, h*3+10), (255,255,255))
    im2.paste(img,(0,0))
    img=pre_hd_ez(img)                              # 二值化黑白图像
    im = Image.new('1', (w, h), 0)

    for i in range(rp):     
        img= pre_jz(img,i)                          # 第i次降噪 
    im2.paste(img,(0,h+5))
    
    letters = find_letters (img)

#在字符之间，将非字符噪点消去
    im_fill = Image.new ('1',(1,h),0)
    for letter in letters:
        w = letter [1] - letter [0]
        if w <= 3:
            for x in range (letter[0],letter[1]+1):
                img.paste(im_fill,(x,0))

#验证码由多个字符组成，每个字符的高度一般都固定，为高度之外的空间消去噪点
    im1 = img.crop((0,h0,img.size[0],h0+height))
    im.paste(im1,(0,h0))
    im2.paste(im,(0,h*2+10))
    return im


def find_letters(im2):                               # 形成单字符图像分割线
    inletter = False
    foundletter=False
    start = 0
    end = 0
    letters = [] #待识别的字符
    for y in range(im2.size[0]): # slice across，
        for x in range(im2.size[1]): # slice down
            pix = im2.getpixel((y,x))
            if pix != 0:
                inletter = True                

        if foundletter == False and inletter == True:
            foundletter = True
            start = y

        if foundletter == True and inletter == False:
            foundletter = False
            end = y-1
            letters.append((start,end)) 

        inletter=False
    if start > end :
        letters.append ((start,y))
    return letters

def blk_points (im):                                # 统计图像中的黑点坐标
    dict = {}
    im = im.convert ('1')
    for x in range(im.size[0]): 
        for y in range(im.size[1]):
            pix = im.getpixel((x,y))
            if pix !=0:
                dict [(x,y)] = 0
    return dict

def in_letter_down(im,xy,inlt,n):                   # 向下收索黑点
    w,h = im.size
    x0,y0 = xy
    F = 0
    pix = im.getpixel((x0,y0))
    if pix == 0:
        return F
    for x in range (x0,w):                          # 向右
        pix = im.getpixel((x,y0))
        if pix == 0:
            break
        if inlt [(x,y0)] != 0 :
            if F == 0 :
                F = inlt [(x,y0)]
        inlt [(x,y0)] = n
    for y in range (y0+1,h):                        # 向下
        pix = im.getpixel((x0,y))
        if pix == 0:
            break
        if inlt [(x0,y)] != 0 :
            F = inlt [(x0,y)]
        inlt [(x0,y)] = n
    return F

def in_letter_up(im,xy,inlt,n):                     # 向上收索黑点
    w,h = im.size
    x0,y0 = xy
    F = 0
    pix = im.getpixel ((x0,y0))
    if pix == 0:
        return F
    for x in range (x0,w):                          # 向右
        pix = im.getpixel((x,y0))
        if pix == 0:
            break
        if inlt [(x,y0)] != 0 :
            F =  inlt [(x,y0)]
        inlt [(x,y0)] = n
        
    for y in range (y0-1,0,-1):                     # 向上收索
        pix = im.getpixel((x0,y))
        if pix == 0:
            break
        if inlt [(x0,y)] != 0 :
            F = inlt [(x0,y)]
        inlt [(x0,y)] = n

    return F


def in_letter(img,point,inlt,n):                    # 遍历图片，找到形成字符的坐标串
    f_down = 0
    f_up = 0
    x0,y0 = point
    f = in_letter_down(img,(x0,y0),inlt,n)          # 起始点
    F = f
    w,h = img.size
    x1,y1 = w - x0, h-y0                            # 向下递归
    if x1 > y1:
        x1 = y1
    for x in range (x1):
        x0 += 1
        y0 += 1
        pix = img.getpixel ((x0,y0))
        if pix == 0:
            break
        f_down  = in_letter_down(img,(x0,y0),inlt,n)
        if f_down != 0:
            F = f_down
        
    x0,y0 = point
    x1 = w - x0                                     # 向上递归
    if x1 > y0:
        x1 = y0
    for x in range(x1):
        x0 += 1
        y0 += -1
        pix = img.getpixel ((x0,y0))
        if pix == 0:
            break
        f_up = in_letter_up(img,(x0,y0),inlt,n)
        if f_up != 0:
            F = f_up
    return F

        



def denoise(img):                                   # 对图像进行遍历降噪
    bkp = blk_points (img)
    n = 0                   # 子串编号
    all_str = []            # 全部子串
    w,h =img.size
    for point in bkp:
        v = bkp [point]
        sub_str =[]
        if v != 0:
            continue
        n += 1
        f = in_letter(img,point,bkp,n)
        for xy in bkp:
            if bkp [xy] == n: 
                sub_str.append (xy) # 得到子串
        if f == 0:                  # 起始位置是否与其他串相邻
            x0,y0 = sub_str[0]
            if x0 > 0:
                x = x0 -1
                if (x,y0) in bkp:
                    f = bkp [(x,y0)]
            if y0 > 0:
                y = y0 - 1
                if (x0,y) in bkp:
                    f = bkp [(x0,y)]

        if f == 0:
            all_str.append(sub_str) # 独立串
        else:
            n -= 1
            all_str[f-1].extend ( sub_str)
            all_str[f-1] = list(set(all_str[f-1])) # 与相邻的串合并

            for xy in sub_str:
                bkp [xy] = f
    all_str.sort(key=len)
    n = 0
    for sub_str in all_str:                         # 查找相交串，然后合并
        for s_str in all_str:
            f = 0
            if sub_str != s_str:
                st  = list (set(sub_str).intersection(set(s_str)))
                if st != []:
                    st = list (set(sub_str).union(set(s_str)))
                    all_str.remove(s_str)
                    all_str.append(st)
                    f =1
        if f == 1:
            all_str[n] = []
        n += 1
    n = 0
    l = len(all_str)

# 删除合并的另一个串
    while n <  l:
        if all_str[n] == []:
            all_str.pop(n)
            n -= 1
            l -= 1
        n += 1

#消除噪点小串
    for sub_str in all_str:
        if len (sub_str) <= 6:
            f = 0
            for (x,y) in sub_str:               # 查找有相邻串的小串，保留
                if y != h and (x,y+1) in bkp and (x,y+1) not in sub_str:
                    f = bkp [x,y+1]
                    break
                if y != 0 and (x,y-1) in bkp and (x,y-1) not in sub_str:
                    f = bkp [x,y-1]
                    break
            if f == 0:
                print('删除独立小串,',sub_str,'\n')
                for point in sub_str:
                    img.putpixel(point,0)
                
    return img
    


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    path_in=path + "/origin_imgs/"      # 原始图片目录
    path_out=path +'/contrast_imgs/'    # 前后比较图片目录
    path_idt=path +'/WB_imgs/'          # 处理完成后的黑白图片目录
    im=Image.open(path_in+'1.png')      # 任取一张典型图片，获取图片尺寸
    repeat = 2                          # 降噪迭代次数
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
        img = noise_clean(img,2,9,12)       # 降噪
        im_new.paste(img,(0,h+5))
        img = denoise (img)                 # 遍历降噪
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
            print ('{: >3d}'.format(im.size [0]),end = '  ')
            num += 1
