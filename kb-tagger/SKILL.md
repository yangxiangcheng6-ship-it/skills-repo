---
name: kb-tagger
description: 智能入库打标专家。为 Dify 知识库文档打标元数据 version/file_role/doc_summary，内置 KB 路由对照表（标准/偏离 × docx/xlsx）、file_role 7 分类法、打标 payload 构造与校验脚本。当用户需要给文档入库打标、更新文档元数据、判断文档角色或版本归属时使用。
---

# 智能入库打标专家（kb-tagger）

## 用途

对知识库文档执行标准化元数据打标，三个字段：

- **version**：文档版本，取值 `标准` / `偏离` —— 通常由用户直接提供，**不要自行猜测**
- **file_role**：文档角色，7 类之一（见 Reference/打标规范.md）
- **doc_summary**：一句话概括，**15 字以内**

## 何时触发

- 用户要"入库 / 打标 / 更新元数据 / 判断文档角色"的知识库文档
- 用户给出文件名与版本（标准/偏离），要求走标准入库打标流程

## 执行流程（严格按顺序）

### 第 1 步：确认输入
必须拿到：文件名 `file_name`（含扩展名 docx/xlsx）、版本 `version`（标准/偏离）。
用户没给版本时先追问，不猜测（补充规则 2：追问时只输出问题，不执行任何其他动作）。

### 第 2 步：查 KB 路由
```bash
python route_cfg.py <file_name> <version>
```
输出 `dataset_id`、`start_node_id`、`version_id`、`file_role_id`、`doc_summary_id`。
对照表覆盖（标准,docx）（标准,xlsx）（偏离,docx）（偏离,xlsx）四类；未匹配时默认（标准,docx）并在结果里给出 `matched:false`。

### 第 3 步：获取文档内容片段
- 文件已上传到会话：`read_temp_file` 读取；或用 `list_temp_files` 确认路径
- 文件不在会话中：用 Dify 检索接口拉取文档内容片段（query 用"概述 范围 定义 条款 义务 责任 安全 数据 价格 服务 协议"，hybrid_search，top_k=5，按 document_name 过滤）

### 第 4 步：判断 file_role 与 doc_summary
```bash
python tag_prompt.py
```
得到 7 分类法提示词模板，把第 3 步内容片段代入，由 LLM 输出：
```json
{"file_role": "7选1", "doc_summary": "15字以内概括"}
```
判断要点：version 已知不判断；file_role 依据文档性质（框架合同→主协议、标准法律条款→通用条款、偏离表→变更协议、报价/价目表→商务附件等）。

### 第 5 步：构造打标 payload
```bash
python build_metadata.py <document_id> <version> <file_role> <doc_summary> <version_id> <file_role_id> <doc_summary_id>
```
输出标准 `metadata_list` JSON（partial_update=true），字段顺序：version → file_role → doc_summary。

### 第 6 步：校验（建议执行）
```bash
python validate_tags.py --file_role <角色> --doc_summary <概括> --version <版本>
```
- file_role 必须在 7 类内
- doc_summary ≤ 15 字
- version ∈ {标准, 偏离}
校验失败先修正再继续。

### 第 7 步：执行打标
调用 Dify 元数据更新接口：
`POST /v1/datasets/{dataset_id}/documents/metadata`
Body 用第 5 步 payload，Authorization: Bearer dataset-key。

## 交付物

- 打标结果汇总：文件名、version、file_role、doc_summary、各字段 ID、更新接口返回状态
- 将结果汇总写入 temp 文件并用 `export_temp_file` 标记交付

## 参考

- `Reference/打标规范.md`：7 分类法详细定义与 doc_summary 示例
- `Scripts/`：route_cfg.py / tag_prompt.py / build_metadata.py / validate_tags.py（全部标准库，无第三方依赖）

## 注意

- 脚本在技能目录下执行，cwd 已在技能包根目录
- 不要修改脚本本身；字段 ID 以 route_cfg.py 输出为准
- doc_summary 是中文概括，不是文件名
- 2026-08-25 发布流水线联调标记：此版本由 git commit 自动部署
