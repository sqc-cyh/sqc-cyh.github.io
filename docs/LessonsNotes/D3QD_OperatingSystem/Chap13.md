---

title: Chap 13 | I/O Systems

hide:
  #  - navigation # 显示右
  #  - toc #显示左
  #  - footer
  #  - feedback  
comments: true  #默认不开启评论

---

<h1 id="欢迎">Chap 13 | I/O Systems</h1>

!!! note "章节启示录"
    <!-- === "Tab 1" -->
        <!-- Markdown **content**. -->
    <!-- === "Tab 2"
        More Markdown **content**. -->
    本章节是OS的第十三章。

## 1.I/O Hardware
More than 200 harddisk manufacturers

* Common concepts
    1. Port 
    2. Bus (daisy chain or shared direct access) 总线
    3. Controller (host adapter)

* 不同的访问方式：
    1. Special I/O instructions 芯片可以控制一些特定的设备（英特尔）
    2. Memory-mapped I/O 更为常见，把重要的地址、寄存器（保存一些控制信息和数据）与内存当中的逻辑地址映射起来。

* 典型的总线结构：      
    ![](./img/138.png){width="400"}

* I/O Port Registers：
    1. Data-in: read by the host to get input
    2. Data-out: written by the host to send output
    3. Status: device status read by the host
    4. Control: written by the host to start a command or change the mode of a device
    
有很多种控制方式：

* Polling：
    1. host反复读busy bit直到bit清除
    2. 设置write bit 到comman 此村其，并write a byte到data-out寄存器
    3. 设置command-ready bit
    4. 发现command-ready是1
    5. 通过data-out 寄存器获取byte并执行I/O
    6. 检查错误，没错误就把busy bit重置

* Interrupt：
    ![](./img/140.png)

* Direct Memory Access：可以让cpu以block的大小处理数据（但必须连续），只在DMA发生的前后才参与
    1. Used to avoid programmed I/O (可编程I/O) for large data movement
    2. Requires DMA controller
    3. Bypasses 旁路 CPU to transfer data directly between I/O device and memory 
    
    ![](./img/139.png)

## 2.Application I/O Interface
* I/O系统调用将设备行为封装在泛型类中，设备驱动层隐藏了内核中I/O控制器之间的差异

* 设备在许多方面都不同
    1. Character-stream or block 字符流或字符块
    2. Sequential or random-access 顺序访问或随机访问
    3. Sharable or dedicated 共享或专用
    4. Speed of operation 运行速度
    5. read-write, read only, or write only 读写、只读、只写（显示器，只能给他传数据）

* A Kernel I/O Structure：通过driver，隐藏了device间的特异性
    ![](./img/141.png)

* Block and Character Devices：
    * 块设备包括磁盘驱动器
        1. 命令包括读、写、查找
        2. 原始I/O或文件系统访问
        3. 内存映射文件访问是可能的

    * 字符设备包括键盘、鼠标、串行端口
        1. 命令包括get、put
        2. 层叠在上面的库允许行编辑

* Network Devices：比较高速的设备
    1. 从块和字符变化足够有自己的接口
    2. Unix和Windows NT/9x/2000包括套接字接口
        1. 将网络协议与网络操作分离
        2. 包括服务器的选择功能
    3. 方法多种多样（pipes、FIFOs、streans、queues、mailboxes）

* Blocking and Nonblocking I/O
    * Blocking - process suspended until I/O completed
        1. 易于使用和理解
        2. 不足以满足某些需求
    * Nonblocking - I/O call returns as much as available
        1. 用户界面，数据拷贝（缓冲I/O）
        2. 通过多线程实现
        3. 快速返回读取或写入的字节数
    * Asynchronous - process runs while I/O executes
        1. 难以使用
        2. I/O子系统在I/O完成时发出信号

    ![](./img/142.png)

## 3.Kernel I/O Subsystem
* Scheduling调度
    1. 一些I/O请求通过每个设备队列排序
        
        >例如，磁盘调度
    
    2. 有些OS尝试公平

* Buffering：在设备之间传输时将数据存储在内存中
    1. 处理设备速度不匹配，例如从调制解调器接收数据到磁盘。
        * 双缓冲技术
    2. 处理设备传输大小不匹配，例如网络数据包
    3. 维护“复制语义”（当write（）系统调用指定一个用于存储数据的缓冲区，并在系统调用后修改其内容时）

* Caching：保存数据副本的快速内存
    1. 永远只是一个副本
    2. 绩效关键

* Spooling假脱机：保持设备的输出
    * 如果设备一次只能处理一个请求
        >例如,印刷

* Device reservation设备保留：提供对设备的独占访问
    1. 系统调用分配和回收
    2. 注意死锁