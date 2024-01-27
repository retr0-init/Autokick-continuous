- [中文](#discord机器人框架模块模板)
- [English](#discord-bot-framework-module-template)

# Discord机器人框架模块模板
这是针对[Discord机器人内核](https://github.com/retr0-init/Discord-Bot-Framework-Kernel.git)配套的模块模板。其开发可以参考[interactions.py](https://interactions-py.github.io/interactions.py/)。

## 开发中需要考虑的事
- 模块主要点在[`main.py`](main.py)中。
- 所有主要的工作都应该在继承自`interactions.Extension`的类中进行。
- 最好在指令基或指令组中定义你的命令。
- 你可以用另一个`.py`文件来定义内部模块函数。这个文件需要与`main.py`同级。注意你要像以下来引入内部模块：
```python
from . import xxx # xxx是内部模块的名字
```
- 在[`requirements.txt`](requirements.txt)中写入模块所需的第三方库。
- 在[`CHANGELOG`](CHANGELOG)中更新改动。
- 在机器人内核文件夹以外的文件访问会被拒绝。
- 外部程序执行会被拒绝。

# Discord-Bot-Framework-Module-Template
This is the module template for [Discord-Bot-Framework-Kernel](https://github.com/retr0-init/Discord-Bot-Framework-Kernel.git). The development refers to [interactions.py](https://interactions-py.github.io/interactions.py/).

## Things to consider for development
- The module's entry point is in [`main.py`](main.py).
- Do all the main work in the class inherited from `interactions.Extension`.
- It's better to define your commands under either a command base or group.
- You can use another `.py` file for internal module under the same directory as `main.py`. Be aware that you need to import it like
```python
from . import xxx # xxx is the internal module script name
```
- Put python module requirements in [`requirements.txt`](requirements.txt). Do NOT delete this file.
- Update your changes in [`CHANGELOG`](CHANGELOG).
- The file access to the files other than the kernel directory will be denied.
- The external program execution will be denied.