---

title: Chap 6 | Process Synchronization

hide:
  #  - navigation # 显示右
  #  - toc #显示左
  #  - footer
  #  - feedback  
comments: true  #默认不开启评论

---

<h1 id="欢迎">Chap 6 | Process Synchronization</h1>

!!! note "章节启示录"
    <!-- === "Tab 1" -->
        <!-- Markdown **content**. -->
    <!-- === "Tab 2"
        More Markdown **content**. -->
    本章节是OS的第六章。

## 1.Background

### 一些定义
* 临界资源：一次仅允许一个进程使用的资源。
* 临界区：进程中访问临界资源的那段代码。
* 进入区：为了进入临界区使用临界资源，在进入区要检查可否进入临界区，若能进入临界区，则应设置正在访问临界区的标志，以防止其他进程同时进入临界区。
* 退出区：将正在访问临界区的标志清除。
* 剩余区：代码的其余部分。  
![](./img/46.png)

!!! question "几个例子：是否为临界资源"
    全局共享变量？是    
    局部变量？ 不是 
    只读数据？ 不是 
    CPU？ 不是（不需要同步机制来保护）  

* 同步（直接制约关系）：为完成某种任务而建立的两个或多个进程，这些进程因为需要协调它们的运行次序而等待、传递信息所产生的制约关系。
* 互斥（间接制约关系）：当一个进程进入临界区使用临界资源时，另一个进程必须等待，当占用临界资源的进程退出临界区后，另一进程才允许访问此临界资源。

!!! example "进程同步的例子"
    进程同步是指在多进程或多线程环境中，为了确保多个进程或线程能够按照一定的顺序或条件正确地访问共享资源而采取的各种协调机制。

    * 使用count来追踪整个buffer
        1. 生产者生产后count++
        2. 消费者消费后count--

    ```c++
    while(true){
        while(count == BUFFER_SIZE);
        buffer[in] = nextProduced;
        in = (in + 1) % BUFFER_SIZE;
        count++;
    }
    ```
    ```c++
    while(true){
        while(count == 0);
        nextConsumed = buffer[out];
        out = (out + 1) % BUFFER_SIZE;
        count--;
    }
    ```
!!! example "进程互斥的例子 Race Condition （竞态条件）"
    竞态条件是指一个内存位置被并发访问，并且至少有一次是写访问。

    * count++ could be implemented as
        1. register1 = count     
        2. register1 = register1 + 1     
        3. count = register1

    * count-- could be implemented as
        1. register2 = count     
        2. register2 = register2 - 1     
        3. count = register2

    如果在抢占式中打乱顺序就会出错    
    ![](./img/45.png){width="500"}


    ??? question "对于访问共享的内核数据(shared kernel data)，非抢占的内核是否受竞态条件(race conditions)的影响？"
        多核情况下，两个进程同时运行时还是有可能出现竞态条件。

### 实现临界区互斥必须遵循的准则
* Solution to Critical-Section Problem：(需要满足以下三个条件)
    1. Mutual Exclusion（互斥）：如果进程Pi在它的临界区执行，那么没有其他进程可以在它们的临界区执行。
    2. Progress（空闲让进）：如果没有进程在其临界区执行，并且有一些进程希望进入其临界区，那么下一个进入临界区的进程的选择不能无限期推迟。
    3. Bounded Waiting（有限等待）：在一个进程请求进入其临界区之后，在该请求被批准之前，允许其他进程进入其临界区的次数必须存在一个界限
    4. 让权等待（原则上应遵循，非必须）：当进程不能进入临界区时，应立即释放处理器，防止进程忙等待。


**以下将介绍实现临界区互斥的几种基本方法**

## 2.软件方法

### 2.1 单标志法   
设置公共整型变量turn，指示允许进入临界区的进程编号  
turn = i时，允许Pi进入临界区         
进程退出临界区时交给另一个进程turn = j

* Process Pi:
```c++
do{
    while(turn != i);
    critical section
    turn=j; 
    remainder section
} while (1);
```

* Process Pj:
```c++
do{
    while(turn != j);
    critical section
    turn=i; 
    remainder section
} while (1);
```

Mutual Exclusion? Yes  
Progress? No  
Bounded Waiting? Yes  

可实现两个进程轮替进入临界区    
必须轮替进入，不满足空闲让进（若某个进程不再进入临界区，则另一个进程也将无法进入临界区）

### 2.2 双标志后检查法
设置布尔型数组flag[2]，用来标记各进程进入临界区的意愿   
flag[i]=true表示进程Pi想进入    
先表达自己进入临界区意愿    
再轮询对方是否想进入，确定对方不想进入后再进入  
访问结束退出后设置flag[i]=false，表示不想进入，允许对方进入

boolean flag[2];  flag[0] = flag[1] = 0;    
flag[i] = true  if Pi tries to enter CS 

* Process Pi:
```c++
do{
    flag[i]=true;//先表达自己的意愿
    while( flag[j] );//再等待对方
    critical section
    flag[i]=false; 
    remainder section
} while (1);
```

* Process Pj:
```c++
do{
    flag[j]=true;
    while( flag[i] );
    critical section
    flag[j]=false; 
    remainder section
} while (1);
```


Mutual Exclusion? Yes   
Progress? No   
Bounded Waiting? Yes(j进入一次后就会轮到i)

可能导致双方都不能进入      
违反空闲让进

### 2.3 双标志先检查法 
设置布尔型数组flag[2]，用来标记各进程进入临界区的意愿flag[i]=true表示进程Pi想进入   
进程进入临界区前先轮询对方是否想进入    
确定对方不想进入后再进入    
访问结束退出后设置flag[i]=false，表示不想进入，允许对方进入

boolean flag[2];  flag[0] = flag[1] = 0;    
flag[i] = true  if Pi tries to enter CS

* Process Pi:
```c++
do{
    while(flag[j]); 
    flag[i]=TRUE; 
    critical section; 
    flag[i] = FALSE; 
    remainder section;
}while(1);
```

* Process Pj:
```c++
do{
    while(flag[i]); 
    flag[j]=TRUE; 
    critical section; 
    flag[j] = FALSE; 
    remainder section;
}while(1);
```

Mutual Exclusion? No (都是false时，就不满足了)
Progress? Yes

不用交替进入    
违反互斥

### 2.4 Peterson’s Solution
结合单标志法和双标志后检查法，首先表达自身意愿(flag[]=true)之后设置自身要进入(turn=0/1)；   
若双方互相确定对方都想进入时，turn只能等于一个值，因此会谦让对方进入    
若一方不想进入，则其flag[i]=false，对方可直接进入   

* Process Pi：
```c++
while (true) {
    flag[i] = TRUE;
    turn = j;
    while ( flag[j] && turn == j);
    CRITICAL SECTION
    flag[i] = FALSE;
    REMAINDER SECTION
}
```

* Process Pj：
```c++
while (true) {
    flag[j] = TRUE;
    turn = i;
    while ( flag[i] && turn == i);
    CRITICAL SECTION
    flag[j] = FALSE;
    REMAINDER SECTION
}
```

Mutual Exclusion? Yes   
Progress? Yes   
Bounded Waiting? Yes    
但依然未遵循“让权等待”原则

* Question:There are no guarantees that Peterson's solution works correctly on modern computer architectures,因为编译时会对代码执行的顺序进行优化，会把load代码放到store代码上面，相当于实际编译时会把 `while ( flag[i] && turn == i);` 放到上面，也就是先执行这一句，这样就会变成先检查法，从而不满足互斥。

* 解决：使用内存栅栏 `asm(“mfence”);` ,放在while语句上方。

### 2.5 Bakery Algorithm (面包房算法) Lamport

* Dijkstra's concurrent programming problem:
    1. 任何时间，最多只能有一个进程进入 critical section；
    2. 每个进程最终都会进入 critical section；
    3. 每个进程都能停在 noncritical section；
    4. 不能对进程的速度做任何假设。

* idea：
    1. 在进入临界区之前，进程接收一个数字。最小数字的持有者进入临界区。
    2. 如果进程Pi和Pj收到相同的数字，如果i < j，则优先服务Pi；否则Pj先上。
    3. 编号方案总是按枚举的递增顺序生成数字；例如：1、2、3、3、3、3、4、5

boolean choosing[n]: 表示进程是否在取号；初始false。    
int number[n]: 记录每个进程取到的号码；初始0。  
（a，b）＜（c，d）: (1) a＜c, or (2) a==c且b＜d 

```c++
do{
    choosing[i] = true;
    number[i] = max{number[0],number[1],...,number[n-1]}+1; //选号码
    choosing[i] = false;
    for(j = 0; j＜n; j++){
        while (choosing[j]);
        while ((number[j] != 0) && (number[j], j)＜(number[i], i));
    };
    CRITICAL SECTION
    number[i] = 0;
    REMAINDER SECTION
} while(1);
```

Mutual Exclusion? Yes  
Progress? Yes  
Bounded Waiting? Yes

## 3.硬件方法
atmoic == non-interruptable

### 2.1 Disable interrupts (关中断法，中断屏蔽法)
* idea：
    1. 进入临界区前直接屏蔽中断，保证临界区资源顺利使用    
    2. 使用完毕，打开中断


```c++
while (true) {
    Disable Interrupts; 
    Critical section;
    Enable Interrupts;
    Remainder section;
}
```

* 缺点：
    1. 可能影响系统效率：滥用关中断会严重影响CPU执行效率，其锁住CPU可能导致原本一些短时间即可完成的需要等待开中断。
    2. 不适用于多CPU系统 ：中断屏蔽法适用于单CPU系统，在多CPU系统中无法有效同步各个CPU的操作。
    3. 安全性问题：滥用关中断权力可能导致严重后果，例如在关闭中断期间，一些重要的中断请求可能被错过，影响系统的稳定性和可靠性。

### 2.2 TestAndSet Instruction
TestAndSet指令是原子操作，其功能是读出指定标志后将该标志设置为真。    

```c++
boolean TestAndSet (boolean *target){
    boolean rv = *target;
    *target = TRUE;
    return rv;
}
```

```c++
while (true) {
    while ( TestAndSet (&lock ));   // do nothing
    //    critical section
    lock = FALSE;
    //    remainder section 
}
```

Mutual Exclusion? Yes
Progress? Yes
Bounded Waiting? No

相比于关中断方法，由于“锁”是共享的，这种方法适用于多处理器系统。但缺点是暂时无法进入临界区的进程会占用CPU循环执行TS指令，因此还是无法实现“让权等待”。

### 2.3 Swap  Instruction

```c++
void Swap(boolean *a, boolean *b){
    boolean temp = *a;
    *a = *b;
    *b = *temp;
}
```

* idea:
    1. 对每个临界资源，swap设置一个全局bool变量lock(初值为false)，每个进程设置局部变量key(初值为true)  
    2. 进程调用swap()指令访问临界区，会交换key和lock的值，实现上锁，进入访问   
    3. 退出时把lock重置为false

```c++
while (true) {
    key = TRUE;
    while (key == TRUE)
        Swap(&lock, &key) ;   
    //    critical section
    lock = FALSE;
    //    remainder section 
}
```
Mutual Exclusion? Yes
Progress? Yes
Bounded Waiting? No

* The compare_and_swap (CAS)  Instruction 
```c++
int compare_and_swap(int *value, int expected, int new_value){ 
    int temp = *value; 
    if (*value == expected) 
        *value = new_value; 
    return temp; 
} 
```
```c++
while (true){
    while (compare_and_swap(&lock, 0, 1) != 0) ;  // do nothing 
    // critical section 
    lock = 0;  
    // remainder section 
} 
```
Mutual Exclusion? Yes
Progress? Yes
Bounded Waiting? No

* Bounded-waiting with compare-and-swap:
```c++
while (true) {         
    waiting[i] = true;         
    key = 1;         
    while (waiting[i] && key == 1) 
        key = compare_and_swap(&lock,0,1); 
    waiting[i] = false; 
    /* critical section */ 
    j = (i + 1) % n; 
    while ((j != i) && !waiting[j]) 
        j = (j + 1) % n; 
    if (j == i) 
        lock = 0; 
    else 
        waiting[j] = false; 
    /* remainder section */ 
}
```

### 2.4 Mutex Locks
```c++
acquire() {
    while (!available); 
    /* busy wait */
    available = false;
}
release() {
    available = true;
}
```

```c++
while (true) { 
    acquire lock
    critical section 
    release lock 
    remainder section 
}
```

### 硬件实现方法总结
* 优点
    1. 适用于任意数目的进程，在单处理器或多处理器上
    2. 简单，容易验证其正确性
    3. 可以支持进程内存在多个临界区，只需为每个临界区设立一个布尔变量
* 缺点
    1. 耗费CPU时间，不能实现“让权等待”
    2. 可能不满足有限等待：从等待进程中随机选择一个进入临界区，有的进程可能一直选不上
    3. 可能死锁

## 4.信号量方法
信号量的含义：通常用信号量表示资源或临界区  
S.value >0 表示有S.value个资源可用; 
S.value=0 表示无资源可用或表示不允许进程再进人临界区；  
S.value<0 则|S.value|表示在等待队列中进程的个数或表示等待进入临界区的进程个数。


* Two indivisible operations modify S: 
    1. wait() and signal()
    2. originally called P() andV() 
    3. Proberen(测试)，Verhogen(增加)

```c++
wait (S) {
     while S <= 0; // no-op
     S--;
}
```
```c++
signal (S) {
    S++;
}
```

* Counting semaphore （计数型）–integer value can range over an unrestricted domain
* Binary semaphore （二进制型）–integer value can range only between 0 and 1; can be simpler to implement   
    Also known as mutex locks
* Can implement a counting semaphore S as a binary semaphore

* Usage as General Synchronization Tool:   
    1. Provides mutual exclusion    
        ```c++
        Semaphore S;    
        wait (S);
        Critical Section
        signal (S);
        Remainder Section
        ```
    2. P1 has a statement S1, P2 has S2.Statement S1 to be executed before S2 
        1. P1:
        ```c++
        S1;
        Signal(S);
        ```
        2. P2:  
        ```c++
        Wait(S);
        S2;
        ```
!!! question "问题？"
    * Four rooms, four identical 一样的 keys. 需要How many semaphore?   
        1 is enough. 将信号量初始值设定为4，代表有4个共享资源可以使用
    * Four rooms, each with a unique key (four different keys)How many semaphore?   
        此时四个房间代表的共享资源可能不一样，需要 4 个信号量，每个信号量初始值设定为1，代表每个指定的房间是否被访问。
        * What if using 1 semaphore?    
            导致多个房间之间的访问冲突，无法保证互斥性。如果两个进程同时访问这个信号量，因为需要 key 与 room 的匹配，两个进程可能会同时check同一个房间，无法保证互斥性。

### Semaphore Implementation with no Busy waiting

* 每个信号量都有一个相关联的等待队列。每个信号量有两个数据项：
    1. value (of type integer)
    2. pointer to a linked-list of PCBs
* 两种操作（作为基本系统调用提供）：    
    1. block(sleep)：将调用该操作的进程放在适当的等待队列上。
    2. wakeup：删除等待队列中的一个进程，并将其放入就绪队列。

* wait：
```c++
wait (S){ 
    value--;
    if (value < 0) { // add this process to waiting queue
        block();  
    }
}
```

* signal:
```c++
Signal (S){ 
    value++;
    if (value <= 0) { // remove a process P from the waiting queue
        wakeup(P);  
    }
}
```

在这种实现中， S 的值可以取负值，当 S 取负时，它的值的绝对值代表排队进程的个数。

```c++
void V(struct semaphore *s){
    acquire(&s->lock);
    s->count += 1;
    wakeup(s);
    release(&s->lock)
}

void P(struct semaphore *s){
    while(s->count == 0)
        sleep(s);
    acquire(&s->lock);
    s->count -= 1;
    release(&s->lock);
}
```

可能会有 lost wake-up 的问题（未sleep的进程先执行了wakeup）

防止wakeup丢失：
```c++
void V(struct semaphore *s){
    acquire(&s->lock);
    s->count += 1;
    wakeup(s);
    release(&s->lock)
}

void P(struct semaphore *s){
    acquire(&s->lock);
    while(s->count == 0)
        sleep(s);
    s->count -= 1;
    release(&s->lock);
}
```
但是这样会deadlock，一直sleep，因为sleep了但却一直没放锁

修改函数，sleep （s, &s->lock）可以在调用进程被标记为休眠并等待wait queue s释放锁。
```c++
void V(struct semaphore *s){
    acquire(&s->lock);
    s->count += 1;
    wakeup(s);
    release(&s->lock)
}

void P(struct semaphore *s){
    acquire(&s->lock);
    while(s->count == 0)
        sleep(s，&s->lock);
    s->count -= 1;
    release(&s->lock);
}
```

* wait、signal操作必须成对出现，有一个wait操作就一定有一个signal操作。一般情况下:当为互斥操作时，它们同处于同一进程;当为同步操作时，则不在同一进程中出现。      
* 如果两个wait操作相邻，那么它们的顺序至关重要，而两个相邻的signa操作的顺序无关紧要。一个同步wait操作与一个互斥wait操作在一起时，<font color = "red">同步wait操作在互斥wait操作前</font>（如果一个进程先请求互斥访问共享资源，然后等待另一个进程完成操作，这可能导致循环等待，从而引发死锁）。


### Bounded-Buffer Problem（生产者-消费者问题）
N buffers, each can hold one item  

* 需要3个信号量：   
    1. Semaphore **mutex** initialized to the value 1
    2. Semaphore **full** initialized to the value 0, counting full items
    3. Semaphore **empty** initialized to the value N, counting empty items.

* The structure of the producer process：
```c++
while (true) {
    //   produce an item
    wait (empty);
    wait (mutex);
    //  add the item to the  buffer
    signal (mutex);
    signal (full);
}
```

* The structure of the consumer process:
```c++
while (true){
    wait (full);
    wait (mutex);
    //  remove an item from  buffer
    signal (mutex);
    signal (empty);
    //  consume the removed item
}
```

### Readers-Writers Problem
* A data set is shared among a number of concurrent processes:（允许多个读者进行读，只允许一个写者写）
    1. Readers – only read the data set; they do not perform any updates
    2. Writers   – can both read and write.

读者优先：当且仅当所有读者都读完后，才能写。    

* Shared Data：
    1. Data set
    2. Semaphore **mutex** initialized to 1, to ensure mutual exclusion when readcount is updated
    3. Semaphore **wrt** initialized to 1.
    4. Integer readcount initialized to 0.

* The structure of a writer process：
```c++
while (true){
    wait (wrt) ;
    //    writing is performed
    signal (wrt) ;
}
```
* The structure of a reader process:
```c++
while (true){
    wait (mutex) ;
    readcount ++ ;
    if (readcount == 1)  wait (wrt) ; //不允许写者写了
    signal (mutex)
    // reading is performed
    wait (mutex) ;readcount-- ;
    if (readcount  == 0)  signal (wrt) ;//允许写者写
    signal (mutex) ;
}
```

### Dining-Philosophers Problem
![](./img/47.png)   
需要同时拿到左右两边的筷子才能吃饭
* Shared data 
    1. Bowl of rice (data set)
    2. Semaphore **chopstick [5]** initialized to 1

* The structure of Philosopher i:
```c++
while (true)  { 
    wait ( chopstick[i] );//拿左边的
    wait ( chopStick[ (i + 1) % 5] );//拿右边的
    //  eat
    signal ( chopstick[i] );//放左边的
    signal ( chopstick[ (i + 1) % 5] );//放右边的
    //  think
}
```
* 问题：死锁
* 解决方式：
    1. 只允许4个同时吃饭；
    2. 其中一位反序拿筷子；
    3. AND信号量；
    4. 奇数ID和偶数ID设置相反拿筷子顺序；

## 5.Monitors方法
Only one process may be active within the monitor at a time     
Monitors是对共享数据结构实施操作的一组过程所组成的资源管理程序。
```c++
monitor monitor-name{
    // shared variable declarations
    procedure P1 (...) { .... }
    ...
    procedure Pn (...) {......}
    Initialization code ( ....) { ... }
    ...
}
```

* Two operations on a condition variable:
    1. x.wait ()：a process that invokes the operation is suspended.
    2. x.signal ()：resumes one of processes (if any) that invoked x.wait ()

    ![](./img/48.png){width="450"}

* Solution to Dining Philosophers:
```c++
monitor DP{ 
    enum { THINKING; HUNGRY, EATING} state [5] ;
    condition self [5];  //philosopher i can delay herself when unable to get chopsticks
    void pickup (int i) { 
        state[i] = HUNGRY;
        test(i);
        if (state[i] != EATING) self [i].wait;
    }
    void putdown (int i) { 
        state[i] = THINKING;// test left and right neighbors
        test((i + 4) % 5);
        test((i + 1) % 5);
    }
    void test (int i) { 
        if ( (state[(i + 4) % 5] != EATING) &&(state[i] == HUNGRY) &&(state[(i + 1) % 5] != EATING) ) {
            state[i] = EATING ;
            self[i].signal () ;
        }
    }
    initialization_code() { 
        for (int i = 0; i < 5; i++)
        state[i] = THINKING;
    }
}
```