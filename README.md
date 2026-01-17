# K3Cloud Python CLI & MCP Server

这是一个基于 Python 的金蝶 K3 Cloud (Kingdee K3 Cloud) 接口工具集。它提供了命令行工具 (CLI) 用于本地测试和脚本调用，同时也包含了一个 Model Context Protocol (MCP) 服务器，允许 AI 助手（如 Trae, Claude Desktop 等）直接调用 K3 Cloud 的功能。

本项目集成了官方 Python SDK (V8.2.0)，支持标准签名和加密 AppSecret 的自动解密。

## 目录

- [安装与配置](#安装与配置)
- [命令行工具 (CLI) 使用指南](#命令行工具-cli-使用指南)
  - [基础用法](#基础用法)
  - [常用命令示例](#常用命令示例)
- [MCP 服务器使用指南](#mcp-服务器使用指南)

---

## 安装与配置

### 1. 环境准备

确保已安装 Python 3.8+。

```powershell
# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件

在 `src` 目录下创建或修改 `config.ini` 文件。

路径: `src/config.ini`

```ini
[k3cloud]
server_url=http://你的服务器IP/K3Cloud/
acct_id=你的数据中心ID
app_id=你的应用ID
app_secret=你的应用密钥(支持明文或加密密文)
user_name=用户名
lcid=2052
org_num=0
```

---

## 命令行工具 (CLI) 使用指南

入口文件为 `src/main.py`。

### 基础用法

```powershell
python src/main.py [全局选项] <命令> [命令参数]
```

**全局选项:**
- `--config <路径>`: 指定配置文件路径 (默认: `src/config.ini`)
- `--debug`: 开启调试模式，打印详细的请求和响应日志

### 常用命令示例

#### 1. 查询库存 (inventory)

查询指定仓库的物料库存。

```powershell
# 查询前 5 条库存数据
python src/main.py inventory --limit 5

# 指定过滤条件 (例如: 仓库编码为 CK001)
python src/main.py inventory --filter-string "FStockID.Fnumber='CK001'"
```

#### 2. 物料查询 (material-bill-query)

使用单据查询接口查询物料基础资料。

```powershell
# 查询前 10 个物料，返回名称和编码
python src/main.py material-bill-query --limit 10 --field-keys "FName,FNumber"
```

#### 3. 保存物料 (material-save)

创建一个新的物料。

```powershell
# 创建一个测试物料
python src/main.py material-save --number "TEST001" --name "测试物料" --create-org-number 100 --use-org-number 100
```

#### 4. 提交物料 (material-submit)

提交已保存的物料。

```powershell
python src/main.py material-submit --number "TEST001"
```

#### 5. 审核物料 (material-audit)

审核已提交的物料。

```powershell
python src/main.py material-audit --number "TEST001"
```

#### 6. 科目余额表查询 (gl-accountbalance)

查询总账科目的余额。

```powershell
python src/main.py gl-accountbalance --start-year 2023 --start-period 1 --limit 5
```

#### 7. 执行任意服务 (execute)

如果预置命令不满足需求，可以调用任意 K3 Cloud WebAPI 服务。

```powershell
# 示例：查询用户信息
python src/main.py execute --service-url "Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.ExecuteBillQuery" --payload-json '{"FormId": "SEC_User", "FieldKeys": "FName", "Limit": 1}'
```

---

## MCP 服务器使用指南

本项目包含一个 MCP (Model Context Protocol) 服务器，允许 AI 助手直接操作 K3 Cloud。

**启动服务:**

```powershell
python src/mcp_server.py
```

**支持的工具 (Tools):**
- `query_inventory`: 查询库存
- `query_bill`: 通用单据查询
- `save_bill`: 保存单据
- `submit_bill`: 提交单据
- `audit_bill`: 审核单据

在 Trae 或 Claude Desktop 的配置中添加此 MCP 服务器即可使用。
