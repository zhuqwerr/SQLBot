# 本地开发运行问题记录

本文记录本次在 Windows 本地运行项目时遇到的问题、判断依据和处理方法。

## 1. Docker Desktop 未启动

现象：

```powershell
docker info --format '{{.OSType}}'
```

报错：

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

原因：

Docker CLI 能找到，但 Docker Desktop 的 Linux Engine 没有运行。

处理：

先启动 Docker Desktop，等状态变为 Running 后再执行：

```powershell
docker info --format '{{.OSType}}'
```

正常情况下应输出：

```text
linux
```

## 2. PowerShell 命令复制方式错误

现象：

把提示符也一起复制执行：

```powershell
PS D:\AI_Projects\SQLBot> docker info --format '{{.OSType}}'
```

报错：

```text
Get-Process: A positional parameter cannot be found that accepts argument 'docker'.
```

原因：

`PS D:\AI_Projects\SQLBot>` 是 PowerShell 提示符，不是命令内容。

处理：

只执行提示符后面的命令：

```powershell
docker info --format '{{.OSType}}'
```

## 3. 本地调试不需要先打包镜像

结论：

开发调试阶段不需要每次都打包 Docker 镜像。当前项目可以本地源码运行：

- 后端：Python / FastAPI / Uvicorn
- 前端：Vue / Vite
- 数据库：PostgreSQL 容器

推荐流程：

1. 本地改前端或后端源码。
2. 用源码方式启动前后端调试。
3. 验证完成后再打包 Linux 镜像。
4. 把镜像或部署包上传服务器部署。

## 4. 后端默认路径是 Linux 路径

现象：

Windows 本地直接启动后端时，会尝试访问类似路径：

```text
/opt/sqlbot/...
```

原因：

项目默认配置面向容器或 Linux 部署环境，部分目录默认值是 Linux 路径。

处理：

本地启动后端时设置运行目录环境变量，指向项目内 `.runtime/sqlbot-dev`：

```powershell
$runtime = "D:\AI_Projects\SQLBot\.runtime\sqlbot-dev"
$env:BASE_DIR = "$runtime\base"
$env:UPLOAD_DIR = "$runtime\data"
$env:EXCEL_PATH = "$runtime\data"
$env:MCP_IMAGE_PATH = "$runtime\images"
$env:LOCAL_MODEL_PATH = "$runtime\models"
$env:SCRIPT_DIR = "$runtime\base\scripts"
$env:ORACLE_CLIENT_PATH = "$runtime\base\db_client\oracle_instant_client"
$env:LOG_DIR = $runtime
```

Oracle Client 本地缺失时日志里会有 `DPI-1047`，当前只是降级为 thin mode，不影响普通登录和页面调试。

## 5. 后端数据库连接依赖本地 PostgreSQL 容器

本地后端连接的是 PostgreSQL：

```text
127.0.0.1:5432
database: sqlbot
user: root
```

如果后端启动失败，需要先确认数据库容器在运行。

本次使用的容器名：

```powershell
docker start sqlbot-postgres
```

## 6. 前端 `npm run dev` 会先跑类型检查

现象：

`npm run dev` 实际会先执行类似：

```text
vue-tsc -b && vite
```

如果只是快速启动调试页面，可以直接启动 Vite：

```powershell
cd frontend
npm exec vite -- --host 127.0.0.1
```

当前前端开发地址：

```text
http://127.0.0.1:5173/
```

## 7. 登录点击无反应的根因是 CORS 白名单

现象：

登录页能打开，但点击登录没有明显反应。

容易误判：

一开始怀疑是账号密码错误。但密码错误时前端应该显示错误提示，所以这不是最符合现象的解释。

实际证据：

后端日志中出现：

```text
OPTIONS /api/v1/system/config/key HTTP/1.1" 400 Bad Request
OPTIONS /api/v1/system/license HTTP/1.1" 400 Bad Request
```

进一步验证：

`localhost` 来源可以通过 CORS：

```powershell
curl.exe -i -X OPTIONS "http://localhost:8000/api/v1/login/access-token" `
  -H "Origin: http://localhost:5173" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: content-type,accept-language"
```

返回 `200 OK`。

但 `127.0.0.1` 来源被拒绝：

```powershell
curl.exe -i -X OPTIONS "http://localhost:8000/api/v1/login/access-token" `
  -H "Origin: http://127.0.0.1:5173" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: content-type,accept-language"
```

返回：

```text
400 Bad Request
Disallowed CORS origin
```

原因：

后端默认只允许：

```text
http://localhost:5173
```

但前端实际从：

```text
http://127.0.0.1:5173
```

打开时，浏览器会把它当成另一个 Origin。带 `Content-Type`、`Accept-Language` 等请求头的接口会触发 CORS 预检，预检失败后真正的登录请求不会发出，所以页面看起来像点击无反应。

处理：

后端启动时增加 CORS 白名单：

```powershell
$env:FRONTEND_HOST = "http://localhost:5173"
$env:BACKEND_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
```

然后重启后端。

验证：

`127.0.0.1:5173` 的预检已经返回：

```text
200 OK
Access-Control-Allow-Origin: http://127.0.0.1:5173
```

## 8. 本地数据库里的 admin 密码与代码默认密码不一致

现象：

登录接口可用，但新默认密码会返回：

```text
账号或密码错误
```

原因：

代码中的默认密码已经改成：

```text
Report@123456
```

但本地 PostgreSQL 数据库是之前初始化的，`sys_user` 表里的 `admin` 密码仍然是旧值。

处理：

本地开发库中只更新 `admin` 这一条记录，把密码重置为当前默认开发密码。

验证：

接口验证结果：

```text
admin / Report@123456 -> 200 OK
```

当前本地登录信息：

```text
账号：admin
密码：Report@123456
```

## 9. 推荐的本地访问地址

为了减少 CORS 和缓存干扰，建议优先使用：

```text
http://localhost:5173/#/login
```

如果使用：

```text
http://127.0.0.1:5173/#/login
```

后端也必须包含对应的 CORS 白名单。

## 10. 当前本地运行状态

已验证：

- 前端页面可访问。
- 后端 `/docs` 可访问。
- license generator 脚本可加载。
- `/api/v1/system/config/key` 可访问。
- `/api/v1/system/license` 可访问。
- `admin / Report@123456` 登录接口返回 `200 OK`。
- `localhost:5173` 和 `127.0.0.1:5173` 的 CORS 预检均已通过。

