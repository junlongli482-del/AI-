## 1.新项目的情况下
# 进入项目文件夹，右键选择"Git Bash Here"

# 初始化git仓库
git init

# 设置用户信息（第一次使用需要）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 添加所有文件
git add .

# 提交第一个版本
git commit -m "v1.0 - 初始版本"

# 连接到GitLab（替换成你的项目地址）
git remote add origin http://localhost:8001/username/project-name.git

# 配置允许HTTP（本地GitLab需要）
git config --global http.sslVerify false

# 推送到GitLab
git push -u origin master

## 2.继续开发的情况下

# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交新版本（写清楚改了什么）
git commit -m "v1.1 - 添加了用户登录功能"

# 推送到GitLab
git push

# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交新版本（写清楚改了什么）
git commit -m "v1.1 - 添加了用户登录功能"

# 推送到GitLab
git push

⏪ 四、版本回退操作
4.1 临时查看老版本（不删除新版本）
Bash

# 查看版本历史
git log --oneline

# 切换到指定版本查看（临时）
git checkout 版本号

# 查看完毕，回到最新版本
git checkout master


# bug解决
C:\A_XM\xm_3\vue3-fastapi-mysql_v1.0>git push -u origin master
error: src refspec master does not match any
error: failed to push some refs to 'http://localhost:8001/root/vue3-fastapi-mysql_v1.0.git'

这是由于没有master分支导致的错误，使用
git branch -a
查看有哪些分支，一般都默认是main分支。
没有master分支，我们要创建分支

创建并切换到新分支（比如 dev）
git checkout -b master

或者只创建不分切换
git branch master

执行 git add . 和 git commit -m "init"