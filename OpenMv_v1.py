# - By: Engou - 周五 10月 5 2018

import sensor, image, time,math

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

wid=50

ROIup=[0,0,320,wid]
ROIdo=[0,240-wid,320,wid]
ROIle=[0,0,wid,240]
ROIri=[320-wid,0,wid,240]

up=0
do=0
le=0
ri=0

deta_theta = 0   #角度差
one_theta = 0    #第一条线的角度
two_theta = 0    #第二条线的角度
min_degree = 0   #角度的最小值
max_degree = 359 #角度的最大值，此处可以改成360，以便更好区分锐角与钝角
flag = 0

threshold = [(0,60)]

clock = time.clock()

while(True):
    clock.tick()
    image = sensor.snapshot()

    lines = image.find_lines()
    if len(lines)== 1:
        print("starght")
    if len(lines) == 2:                 #如果有第二条线
        one_theta = lines[0].theta()    #给第一条线赋值
        two_theta = lines[1].theta()    #给第二条线赋值
    deta_theta=one_theta-two_theta      #做差求出两条直线的角度差
    if(deta_theta<0):                   #取正
        deta_theta=-deta_theta

    if len(image.find_blobs(threshold,roi=ROIup,merge=True))==1:
        up=1
    if len(image.find_blobs(threshold,roi=ROIdo,merge=True))==1:
        do=1
    if len(image.find_blobs(threshold,roi=ROIle,merge=True))==1:
        le=1
    if len(image.find_blobs(threshold,roi=ROIri,merge=True))==1:
        ri=1

    if up==1 and do==1 :
        print("starght")

    if deta_theta==90:


        if do==1 and ri==1 :
            print("right")
        if do==1 and le==1:
            print("left")
        if do==1 and up==1 and ri==1 and le==1 :
            print("decide")
    else:
        if le==1 and do==1:
            print("45left")
        if ri==1 and do==1:
            print("45right")

    up=0
    do=0
    le=0
    ri=0
