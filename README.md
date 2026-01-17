# K3Cloud Python CLI

这是一个基于 Python 的金蝶 K3 Cloud (Kingdee K3 Cloud) 命令行工具。它集成了官方 Python SDK，提供了便捷的命令行接口用于查询数据，并支持自动导出结果到 Excel。

## 功能特性

- **数据查询**: 支持通过命令行查询业务单据（支持 `inventory` 即时库存, `purchase-order` 采购订单, `purchase-in` 采购入库单, `sales-order` 销售订单, `sales-out` 销售出库单）。
- **自动 Excel 导出**: 查询结果会自动保存为 Excel 文件，支持追加模式。
- **配置灵活**: 支持通过配置文件管理连接信息，支持加密的 AppSecret。
- **SDK 集成**: 基于官方 `kingdee.cdp.webapi.sdk` 构建。

## 目录

- [安装](#安装)
- [配置](#配置)
- [使用指南](#使用指南)

---

## 安装

1. 确保已安装 Python 3.10+。

2. 安装项目依赖：

   ```cmd
   pip install -r requirements.txt
   ```

   > 注意：依赖中包含本地 wheel 包 `libs/kingdee.cdp.webapi.sdk-8.2.0-py3-none-any.whl`，请确保该文件存在。

---

## 配置

在 `src` 目录下创建 `config.ini` 文件（如果不存在）。

**文件路径**: `src/config.ini`

```ini
[k3cloud]
server_url=http://你的服务器IP/K3Cloud/
acct_id=你的数据中心ID
app_id=你的应用ID
app_secret=你的应用密钥
user_name=用户名
lcid=2052
org_num=0
# 可选：指定 Excel 输出文件路径。如果不指定，默认保存在 excel/ 目录下自动生成的文件中
# excel_file=D:/data/k3cloud_data.xlsx
```

---

## 使用指南

工具入口为 `src/main.py`。

### 基础用法

```cmd
python src/main.py [全局选项] <命令> [命令参数]
```

**全局选项:**
- `--config <路径>`: 指定配置文件路径 (默认: `src/config.ini`)
- `--debug`: 开启调试模式，打印详细日志

### 命令详解

#### 1. 即时库存查询 (inventory)

查询库存数据，支持分页和过滤。

```cmd
# 查询前 10 条库存数据
python src/main.py inventory --limit 10

# 查询特定仓库的库存 (使用 filter-string)
python src/main.py inventory --filter-string "FStockID.FNumber='CK001'"

# 查询所有库存 (limit设为0，会自动分页拉取所有数据)
python src/main.py inventory --limit 0
```

**默认查询字段**: 
`FmaterialID.Fnumber,FmaterialID.FName,FStockID.Fnumber,FStockID.Fname,fbaseqty,FModel`

可以通过 `--field-keys` 参数覆盖默认字段：

```cmd
python src/main.py inventory --limit 5 --field-keys "FMaterialID.FNumber,FBaseQty"
```

#### 2. 采购订单查询 (purchase-order)

查询采购订单数据。

```cmd
python src/main.py purchase-order --limit 0
```

#### 3. 采购入库单查询 (purchase-in)

查询采购入库单数据。

```cmd
python src/main.py purchase-in --limit 0
```

#### 4. 销售订单查询 (sales-order)

查询销售订单数据（默认按日期倒序 `FDate DESC`，优先返回最新单据）。

```cmd
python src/main.py sales-order --limit 10
```

**自定义查询字段**:
如果需要查询特定字段，可以使用 `--field-keys` 参数指定（多个字段用逗号分隔）。
例如：
```cmd
python src/main.py sales-order --limit 10 --field-keys "FBillNo,FDate,FCustId,FAmount"
```

#### 5. 销售出库单查询 (sales-out)

查询销售出库单数据。

```cmd
python src/main.py sales-out --limit 0
```

### 结果输出

- **Excel 文件**: 
  - 如果在 `config.ini` 中配置了 `excel_file`，则会追加到该文件中。

## 开发说明

本项目核心逻辑位于 `src/` 目录：
- `main.py`: 程序入口，处理参数解析。
- `commands.py`: 注册和处理具体命令。
- `client.py`: 封装 K3Cloud SDK 调用。
- `config.py`: 配置加载。
- `logger.py`: 日志模块封装。
