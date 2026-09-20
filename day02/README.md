# 第 2 天 · Git 与 GitHub

这一天没有写代码，做的是打通「本地 → 云端」的流程。

## 完成的事
- 安装 Git，配置身份（user.name / user.email）
- 注册 GitHub，创建仓库 python-practice
- 把本地代码推送到 GitHub
- 配置 git 代理（本机代理端口 127.0.0.1:7897）

## 踩过的坑（记下来，避免重复踩）

**1. 在错误的目录执行了 git 命令**
当时终端开在 `D:\软件\Microsoft VS Code`，我却在里面跑了 `git init` 和 `git add .`，
结果把 VS Code 自己的程序文件加进了仓库。

> 教训：敲任何 git 命令之前，先 `pwd` 确认自己在哪。

**2. `git push` 报错 `Connection was reset`**
原因是浏览器会走系统代理，但 git 不会自动走。所以浏览器能打开 GitHub，git 却连不上。

> 解决：`git config --global http.proxy http://127.0.0.1:7897`

## 每天提交三连

```
pwd                      # 先确认目录
git status               # 看改了哪些文件
git add .
git commit -m "说明"
git push
```
