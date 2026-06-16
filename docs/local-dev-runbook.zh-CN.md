# SQLBot 本地调试运行手册（Windows）

本文记录在 Windows 本地用源码方式调试 SQLBot 的启动、验证和关闭流程。

## 1. 前提

本地需要具备：

- Docker Desktop，并且 Linux Engine 已启动。
- Node.js / npm。
- Python 后端虚拟环境：`backend/.venv`。
- 项目目录：`D:\AI_Projects\SQLBot`。

进入项目目录：

```powershell
cd D:\AI_Projects\SQLBot
```

确认 Docker 当前是 Linux Engine：

```powershell
docker info --format '{{.OSType}} {{.ServerVersion}}'
```

正常应输出类似：

```text
linux 29.5.2
```

## 2. 启动 PostgreSQL 容器

本地开发使用的 PostgreSQL 容器名是：

```text
sqlbot-postgres
```

启动容器：

```powershell
docker start sqlbot-postgres
```

检查容器状态：

```powershell
docker ps --format "{{.Names}} {{.Status}}"
```

应能看到：

```text
sqlbot-postgres Up ...
```

本地后端连接参数：

```text
POSTGRES_SERVER=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=sqlbot
POSTGRES_USER=root
POSTGRES_PASSWORD=Password123@pg
```

## 3. 准备本地运行目录

后端默认配置偏向 Linux 容器路径，例如 `/opt/sqlbot/...`。Windows 本地调试时使用项目内的 `.runtime/sqlbot-dev` 作为运行目录。

如果目录不存在，先创建：

```powershell
$runtime = "D:\AI_Projects\SQLBot\.runtime\sqlbot-dev"
New-Item -ItemType Directory -Force "$runtime\base" | Out-Null
New-Item -ItemType Directory -Force "$runtime\data" | Out-Null
New-Item -ItemType Directory -Force "$runtime\images" | Out-Null
New-Item -ItemType Directory -Force "$runtime\models" | Out-Null
New-Item -ItemType Directory -Force "$runtime\logs" | Out-Null
```

## 4. 启动后端

在项目根目录执行：

```powershell
$root = "D:\AI_Projects\SQLBot"
$runtime = Join-Path $root ".runtime\sqlbot-dev"

$env:BASE_DIR = Join-Path $runtime "base"
$env:UPLOAD_DIR = Join-Path $runtime "data"
$env:EXCEL_PATH = Join-Path $runtime "data"
$env:MCP_IMAGE_PATH = Join-Path $runtime "images"
$env:LOCAL_MODEL_PATH = Join-Path $runtime "models"
$env:SCRIPT_DIR = Join-Path $runtime "base\scripts"
$env:ORACLE_CLIENT_PATH = Join-Path $runtime "base\db_client\oracle_instant_client"
$env:LOG_DIR = $runtime
$env:LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s:%(lineno)d - %(message)s"

$env:POSTGRES_SERVER = "127.0.0.1"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_USER = "root"
$env:POSTGRES_PASSWORD = "Password123@pg"
$env:POSTGRES_DB = "sqlbot"

$env:FRONTEND_HOST = "http://localhost:5173"
$env:BACKEND_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

Start-Process `
  -FilePath "$root\backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","main:app","--host","127.0.0.1","--port","8000" `
  -WorkingDirectory "$root\backend" `
  -WindowStyle Hidden `
  -RedirectStandardOutput "$runtime\backend.out.log" `
  -RedirectStandardError "$runtime\backend.err.log"
```

验证后端：

```powershell
curl.exe -i http://127.0.0.1:8000/docs
```

返回 `200 OK` 即表示后端可访问。

查看后端日志：

```powershell
Get-Content -Path .runtime\sqlbot-dev\backend.err.log -Tail 120
Get-Content -Path .runtime\sqlbot-dev\backend.out.log -Tail 80
```

说明：

- 日志中出现 Oracle `DPI-1047` 时，表示本地没有 Oracle Client，后端会降级 thin mode。普通登录和页面调试不受影响。
- 如果端口 `8000` 已被占用，先执行本文最后的关闭命令。

## 5. 启动前端

前端开发接口地址配置在：

```text
frontend/.env.development
```

当前配置：

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=智能报表问数平台 (Development)
```

启动 Vite：

```powershell
cd D:\AI_Projects\SQLBot\frontend
npm exec vite -- --host 127.0.0.1
```

如果需要后台运行并写日志：

```powershell
$root = "D:\AI_Projects\SQLBot"
$runtime = Join-Path $root ".runtime\sqlbot-dev"

Start-Process `
  -FilePath "npm" `
  -ArgumentList "exec","vite","--","--host","127.0.0.1" `
  -WorkingDirectory "$root\frontend" `
  -WindowStyle Hidden `
  -RedirectStandardOutput "$runtime\vite.out.log" `
  -RedirectStandardError "$runtime\vite.err.log"
```

访问前端：

```text
http://localhost:5173/#/login
```

或者：

```text
http://127.0.0.1:5173/#/login
```

建议优先使用 `localhost`。如果使用 `127.0.0.1`，后端必须配置：

```text
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 6. 登录信息

本地开发库当前登录信息：

```text
账号：admin
密码：Report@123456
```

注意：

如果使用旧数据库，密码可能仍是旧初始化值。镜像或代码里的 `DEFAULT_PWD` 不会自动覆盖已经存在的数据库用户密码。

## 7. 验证接口链路

验证 license/config 接口：

```powershell
curl.exe -i http://localhost:8000/api/v1/system/config/key
curl.exe -i http://localhost:8000/api/v1/system/license
```

验证 CORS 预检：

```powershell
curl.exe -i -X OPTIONS "http://localhost:8000/api/v1/login/access-token" `
  -H "Origin: http://127.0.0.1:5173" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: content-type,accept-language"
```

正常应返回：

```text
200 OK
Access-Control-Allow-Origin: http://127.0.0.1:5173
```

如果返回：

```text
400 Bad Request
Disallowed CORS origin
```

说明后端 CORS 启动参数缺少当前前端地址。

## 8. 关闭本地调试服务

关闭前端 Vite 和后端 Uvicorn：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'uvicorn|vite' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

停止 PostgreSQL 容器：

```powershell
docker stop sqlbot-postgres
```

如果本地还运行了完整 SQLBot 容器，也可以停止：

```powershell
docker stop sqlbot
```

一键关闭：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'uvicorn|vite' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

docker stop sqlbot-postgres
docker stop sqlbot
```

如果 `docker stop sqlbot` 提示容器不存在，可以忽略。

## 9. 常见问题

### 9.1 点击登录没有反应

优先检查 CORS。常见原因是：

- 前端从 `http://127.0.0.1:5173` 打开。
- 后端只允许 `http://localhost:5173`。

解决：

后端启动时设置：

```powershell
$env:BACKEND_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
```

然后重启后端。

### 9.2 密码错误但代码默认密码已修改

原因：

已有数据库里的 `sys_user.password` 不会随代码默认值自动变化。

处理：

可以在页面里重置密码，或者直接更新本地开发库中的用户密码。

### 9.3 前端 `npm run dev` 很慢

项目脚本可能先执行类型检查：

```text
vue-tsc -b && vite
```

快速调试页面时可以直接执行：

```powershell
npm exec vite -- --host 127.0.0.1
```

### 9.4 构建镜像时上下文过大

`.dockerignore` 应排除本地运行产物：

```text
.runtime
.git
.github
.idea
frontend/node_modules
frontend/dist
```

