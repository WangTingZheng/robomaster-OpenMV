# robomaster-OpenMV
a project of robomaster 2019 on Intramural race

![head](https://ksr-ugc.imgix.net/assets/022/418/689/2babfabc079b82a2ab8eb527a589baf0_original.jpg?ixlib=rb-1.1.0&w=680&fit=max&v=1535845522&auto=format&gif-q=50&q=92&s=d00b5c3ecc28b8c4790e0705a959730a)

为了迎接实验室举办的robomaster校内赛，我负责建造一个利用图像识别循迹的小车，来应对90度甚至135度的大转弯，与此同时，还可能面临一些其它识别。我主要要研究的是如何利用OpenMV来识别路况，通过uart串口协议指挥stm32来控制小车进行一系列的动作。
<!-more->
#### 一、创建deta.py文档，实现识别一个角的角度

```python
# deta.py - By: Engou - 周日 9月 31 2018
#本脚本能实现画出图中的直线并求出最先发现的两条直线的角度差
import sensor, image, time  #包含进一些模块

deta_theta = 0   #角度差
one_theta = 0    #第一条线的角度
two_theta = 0    #第二条线的角度
min_degree = 0   #角度的最小值
max_degree = 359 #角度的最大值，此处可以改成360，以便更好区分锐角与钝角
flag = 0

sensor.reset()   #一些初始化操作
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    lines = img.find_lines()
    if len(lines) == 2:                 #如果有第二条线
        one_theta = lines[0].theta()    #给第一条线赋值
        two_theta = lines[1].theta()    #给第二条线赋值
    deta_theta=one_theta-two_theta      #做差求出两条直线的角度差
    if(deta_theta<0):                   #取正
        deta_theta=-deta_theta
    #print(clock.fps())
    #下面是显示直线到画面的模块，具体就不解释了
    for l in img.find_lines(threshold = 1000, theta_margin = 25, rho_margin = 25):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            img.draw_line(l.line(), color = (255, 0, 0))
    print(deta_theta)                   #在串口上连续输出角度差
```

该工程的目的是识别robomaster校内赛上不同的线路情况，以便进行相应的操作。不同的道路标示主要有以下四种：

![1](https://i.loli.net/2018/09/30/5bb0e4c980ccd.png)

目前deta.py还不能识别十字路口，也没办法判断路况的方向，因为它是根据判断角度来进行识别的

#### 二、利用ROI(Region of interest)

我了解到，可以设置一个感兴趣的区域，对这个区域单独进行操作，于是我有了一个新的思路：

##### **1.首先我们要用到直线识别**

使用find_lines函数找出屏幕中所有的直线，对于上图的四种情况，在理想状态下有两个取值：1和2。直线是1，锐角、十字、直角都是2，这样我们可以排除直线；

我们再根据find_lines函数返回的直线角度值进行进一步判断。在理想条件下，如果两条直线的夹角小于90度的话，那这个图形一定是锐角，这样我们排除了锐角的情况；

##### **2.从现在开始需要用到ROI**

我们把屏幕分割成以下四个区域

![无标题.png](https://i.loli.net/2018/10/05/5bb76fabc939e.png)



我们知道，图像一定会经过它们四个中的某几个的，对于十字来讲，它穿过的区域有上、下、左、右，对于直角来讲，它穿过的区域有左、下或者右、下，这样我们也可以区分十字和直角了。

##### 3.**接下来我们要判断它们的方向(不包括直线和十字)**

对于锐角和直角，我们都采取相似的算法

我们采用函数find_blobs函数获取roi内的直线区块的值，我们需要的是它的个数，如果一个roi内有直线，也就是直线的区块的数量为1，相应的flag值就被赋值为1

如果下边和右边的直线存在的话，说明它是朝右的，如果是下边和左边的直线存在的话，说明它是朝左的。

至此，我们已经能完全分辨以上四个物体，而且还能区分它们的反向（如果有的话）

#### **4.我把以上算法写成程序**

```python
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
        print("starght") 		#直角

    if deta_theta==90:


        if do==1 and ri==1 :
            print("right")		#直角朝右
        if do==1 and le==1:
            print("left") 		#直角朝左
        if do==1 and up==1 and ri==1 and le==1 :
            print("decide")  	#十字
    else:
        if le==1 and do==1:
            print("45left")   #锐角朝左
        if ri==1 and do==1:
            print("45right") #锐角朝右

    up=0
    do=0
    le=0
    ri=0

```

#### 三.该程序还还有许多需要改进的地方，主要有：

##### 1.**ROI区域的划分**

如果ROI的区域划分得太小，识别的可留误差会变小，在这个时候一旦识别不到，就会出现失误，如果ROI的区域划分太大，容易出现错位，我们知道，图像不一定是在正中央的，所以，ROI的选取需要一个实验的过程，要不断的调整程序中`wid` 的值来获得一个最佳的ROI空间。

##### **2.锐角和直角的区分**

锐角和直角的划分是根据直线识别函数取得的角度差来判定的，在现实情况下，直角可能不是90度，锐角也不一定是45度，甚至有可能大于90度，这些误差是需要后继调整的

##### **3.光线问题**

图像识别的缺点就是受光线影响太大，在之前的程序测试的时候这种问题已经显现，其实也比较好解决，只要打一些辅助灯光就ok，OpenMV也自带led，但最怕的是到时候比赛的环境有所变化，影响到图像识别的精度。

##### **4.处理误差问题**

由于有以上的误差存在，图像识别的结果不会百分之百准确，但我们的小车接收到的转向指令需要百分之百准确，对于这些误差，我们无法百分之百消除，只能利用算法和统计来抵消，这一点需要将来不断完善。















