# SQLBot Podman 离线部署记录（/mnt/cszh）

本文记录本次服务器上的正确部署流程。适用环境：

- 系统使用 Podman，并通过 `docker` 命令模拟 Docker CLI。
- 根分区空间不足，不能使用默认 `/var/lib/containers/storage` 拉取或导入 SQLBot 镜像。
- 大容量磁盘挂载在 `/mnt/cszh`。
- SQLBot 镜像包已经提前下载并传到服务器：`/mnt/cszh/sqlbot.tar`。
- 现有 `gogs` 容器继续保留在默认 Podman 存储中，不迁移。

## 1. 确认环境

```bash
docker --version
podman info --format '{{.Store.GraphRoot}}'
df -h /
df -h /mnt/cszh
podman ps -a
```

当前环境中 `docker --version` 输出类似：

```text
Emulate Docker CLI using podman.
podman version 4.9.4-rhel
```

这表示实际运行时是 Podman。

## 2. 创建目录

SQLBot 镜像存储、临时目录、业务数据全部放到 `/mnt/cszh`。

```bash
mkdir -p /mnt/cszh/sqlbot-podman/storage
mkdir -p /mnt/cszh/sqlbot-podman/runroot
mkdir -p /mnt/cszh/podman-tmp

mkdir -p /mnt/cszh/sqlbot/data/sqlbot/{excel,file,images,logs}
mkdir -p /mnt/cszh/sqlbot/data/postgresql

chmod 1777 /mnt/cszh/podman-tmp
```

说明：

- `/mnt/cszh/sqlbot-podman/storage`：SQLBot 专用 Podman 镜像/容器存储。
- `/mnt/cszh/sqlbot-podman/runroot`：SQLBot 专用运行时目录。
- `/mnt/cszh/podman-tmp`：Podman 解压镜像时使用的临时目录，避免写满 `/var/tmp`。
- `/mnt/cszh/sqlbot/data`：SQLBot 持久化数据目录。

## 3. 配置固定密钥

正式使用必须固定 `SECRET_KEY`。如果不设置，SQLBot 每次启动会在内存中随机生成，重启后可能导致登录 Token 失效，并可能影响已加密的大模型 API Key 等配置。

生成一次密钥：

```bash
openssl rand -hex 32
```

将输出保存到文件：

```bash
vi /mnt/cszh/sqlbot/SECRET_KEY.txt
```

文件中只放一行 64 位随机字符串，不要加 `SECRET_KEY=` 前缀。

设置权限：

```bash
chown root:root /mnt/cszh/sqlbot/SECRET_KEY.txt
chmod 600 /mnt/cszh/sqlbot/SECRET_KEY.txt
```

验证文件存在，但不要把密钥打印到公共终端或聊天记录：

```bash
test -s /mnt/cszh/sqlbot/SECRET_KEY.txt && echo "SECRET_KEY saved"
```

## 4. 清理失败导入残留

如果之前导入或拉取镜像失败，并出现 `/var/tmp/container_images_storage... no space left on device`，先确认没有正在运行的导入任务：

```bash
ps -ef | grep '[p]odman.*load'
ps -ef | grep '[p]odman.*pull'
```

没有输出后清理失败残留：

```bash
rm -rf /var/tmp/container_images_storage*
```

检查根分区：

```bash
df -h /
```

## 5. 导入离线镜像

镜像包路径：

```bash
/mnt/cszh/sqlbot.tar
```

检查文件：

```bash
ls -lh /mnt/cszh/sqlbot.tar
file /mnt/cszh/sqlbot.tar
```

导入镜像。必须带 `TMPDIR`、`--root`、`--runroot`：

```bash
TMPDIR=/mnt/cszh/podman-tmp \
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  load -i /mnt/cszh/sqlbot.tar
```

查看导入后的镜像名称：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  images
```

后续启动命令最后一行要使用这里显示的镜像名。常见为：

```text
docker.io/dataease/sqlbot:latest
```

## 6. 启动 SQLBot

以下命令不使用 `--env-file`，避免 env 文件格式问题。密钥从 `/mnt/cszh/sqlbot/SECRET_KEY.txt` 读取。

```bash
TMPDIR=/mnt/cszh/podman-tmp \
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  run -d \
  --name sqlbot \
  --restart unless-stopped \
  --privileged=true \
  -p 8000:8000 \
  -p 8001:8001 \
  -v /mnt/cszh/sqlbot/data/sqlbot/excel:/opt/sqlbot/data/excel:Z \
  -v /mnt/cszh/sqlbot/data/sqlbot/file:/opt/sqlbot/data/file:Z \
  -v /mnt/cszh/sqlbot/data/sqlbot/images:/opt/sqlbot/images:Z \
  -v /mnt/cszh/sqlbot/data/sqlbot/logs:/opt/sqlbot/app/logs:Z \
  -v /mnt/cszh/sqlbot/data/postgresql:/var/lib/postgresql/data:Z \
  -e SECRET_KEY="$(cat /mnt/cszh/sqlbot/SECRET_KEY.txt)" \
  -e SERVER_IMAGE_HOST="http://223.109.220.142:8001/images/" \
  docker.io/dataease/sqlbot:latest
```

如果 `podman images` 显示的镜像名不是 `docker.io/dataease/sqlbot:latest`，替换启动命令最后一行。

## 7. 查看状态和日志

因为 SQLBot 使用独立 Podman 存储，普通 `podman ps` 看不到它。管理 SQLBot 必须带同样的 `--root` 和 `--runroot`。

查看容器：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  ps -a
```

查看日志：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  logs -f sqlbot
```

日志中出现以下内容表示后端和 MCP 服务已启动：

```text
Uvicorn running on http://0.0.0.0:8001
SQLBot 初始化完成
Uvicorn running on http://0.0.0.0:8000
```

如果 PostgreSQL 日志偶尔出现：

```text
FATAL: database "root" does not exist
```

这通常是某个探测命令未指定数据库名导致 PostgreSQL 尝试连接同名数据库 `root`，不代表 SQLBot 启动失败。SQLBot 使用的数据库是 `sqlbot`。

## 8. 访问系统

浏览器访问：

```text
http://223.109.220.142:8000/
```

默认账号：

```text
用户名：admin
密码：SQLBot@123456
```

首次登录后按系统要求修改密码。

如无法访问，检查服务器防火墙和云安全组是否放行：

- TCP `8000`
- TCP `8001`

firewalld 示例：

```bash
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=8001/tcp
firewall-cmd --reload
```

## 9. 停止并重新运行

停止容器：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  stop sqlbot
```

启动已存在容器：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  start sqlbot
```

重启已存在容器：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  restart sqlbot
```

如果需要删除容器后重新创建：

```bash
podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  stop sqlbot

podman \
  --root /mnt/cszh/sqlbot-podman/storage \
  --runroot /mnt/cszh/sqlbot-podman/runroot \
  rm sqlbot
```

然后重新执行第 6 节启动命令。删除容器不会删除 `/mnt/cszh/sqlbot/data` 下的持久化数据。

## 10. 常用别名

为了减少重复参数，可以创建别名：

```bash
echo "alias sqlbot-podman='podman --root /mnt/cszh/sqlbot-podman/storage --runroot /mnt/cszh/sqlbot-podman/runroot'" >> /root/.bashrc
source /root/.bashrc
```

之后可使用：

```bash
sqlbot-podman ps -a
sqlbot-podman logs -f sqlbot
sqlbot-podman restart sqlbot
```

现有 Gogs 仍使用默认 Podman 存储，继续用普通命令管理：

```bash
podman ps
podman logs gogs
```

## 11. 备份内容

至少备份以下内容：

```text
/mnt/cszh/sqlbot/SECRET_KEY.txt
/mnt/cszh/sqlbot/data/
```

`SECRET_KEY.txt` 必须长期保存。升级、删除重建容器时继续使用同一个密钥。

不要备份到公开仓库，不要发送到聊天记录。
