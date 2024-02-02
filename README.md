# Discord自动踢人模块
1. 在内核中加载后，用以下命令来初始化模块。第一个参数为消息数量阀值，可忽略，默认值为10。第二个参数为天数阀值，可忽略，默认值为30。
```
/autokick setup 10 30
```
2. 使用以下命令让一些身份组不会被此系统自动踢掉：
```
/autokick exclude <身份组0> <身份组1> ...
```
3. 当初始化完成后，用`/autokick start`开启功能。
4. 如果想停止这个系统，用`/autokick stop`指令。

# Discord AutoKick Module
1. After being loaded in the kernel, setup the function with the command below. The first optional parameter is the message count threshold default to 10. The second optional one is the day count threshold default to 30.
```
/autokick setup 10 30
```
2. Use the following command to prevent certain roles from being automatically kicked by this system:
```
/autokick exclude <Role0> <Role1> ...
```
3. After the setup is completed, use `/autokick start` to start the function.
4. If you want to stop the system, use `/autokick stop`.