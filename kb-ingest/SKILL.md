---
name: kb-ingest
description: 智能入库全流程专家。文档（docx/pdf 等）→ MinerU 解析 → md_cleaner 清洗 → Dify MinerU 库建文档（create-by-text）→ 元数据打标（version/file_role/doc_summary/doc_type）→ MinIO 入桶（含清洗后 md 与对象索引 _index.json 同步）。内置路由表（标准/偏离 × 老库/MinerU 库及全部字段 ID）、create-by-text body 构造、索引更新脚本。当用户需要把新文档入库、上传解析打标、同步 MinIO 差异对比数据时使用。不适合：仅打标已有文档（用 kb-tagger）、检索问答（用 kb-qa）。
---

# 智能入库全流程专家（kb-ingest）

把一份源文档完整走完入库链路：MinerU 解析 → 清洗 → MinerU 库建文档 → 打标 → MinIO 入桶 + 索引同步。机械步骤（路由/构造 body/建文档/打标/索引/读写 MinIO）由脚本完成，判断步骤（file_role/doc_summary/doc_type 语义判断）由 LLM 完成。

## 何时触发

- 用户要求"入库 / 上传文档 / 新增到知识库"，给了文件与版本（标准/偏离）
- 用户要求同步 MinIO 差异对比数据（清洗后 md + 索引 _index.json）
- 用户要求判断文档角色/版本归属并入库

**话题过滤**：只处理入库链路。已有文档改元数据 → kb-tagger；检索/问答 → kb-qa；对比 → diff-expert。

## 执行流程（严格按顺序）

### 第 1 步：确认输入

必须拿到：文件名 `file_name`（含扩展名）、版本 `version`（标准/偏离）。用户没给版本时先追问，不猜测。

### 第 2 步：查路由配置

```bash
python Scripts/ingest_cfg.py <version>
```

输出 `dataset_id`（老库管道）、`mineru_dataset_id`（MinerU 库 create-by-text）及全部字段 ID。
- 扩展名不是 xlsx 时走 MinerU 链（第 3~7 步）；**xlsx 不走 MinerU**（MinerU 不支持），直接走老库管道入库 + 打标（打标见 kb-tagger 或第 6 步的 build_metadata 空 payload 分支）

### 第 3 步：MinerU 解析 + 清洗（Dify 插件节点，非脚本）

在 Dify 工作流内用插件完成：`Parse File`（mineru:0.5.0，凭据 server_type=remote / base_url=https://mineru.net / token）→ `清洗 Markdown 文档`（md_cleaner，注意装 0.0.5+，0.0.4 会把处理日志混进正文污染文本）。拿到的清洗后文本保存到本地文件 `cleaned.md`。

> 在 skill_agent 场景外（纯脚本环境）无此插件时：用 MinerU 官方 API（mineru.net）把源文档转成 markdown，再按 Reference/入库全流程.md 的清洗要点做本地清洗。

### 第 4 步：构造 create-by-text body 并建文档

```bash
python Scripts/create_by_text.py <cleaned.md> <file_name> <mineru_dataset_id>
```

输出 `request_body`（检索配置自动：bge-m3 + hybrid 0.7/0.3 + qwen3-rerank + top_k 5 + 0.5，分段 \n\n/500/50）。
- `request_body` 为空（文本空守卫）→ 跳过建文档，直接走第 7 步索引，不入库
- 非空 → 调 `POST /v1/datasets/{mineru_dataset_id}/document/create-by-text`（Authorization: Bearer dataset-key），保存响应

### 第 5 步：取 document_id

```bash
python Scripts/extract_doc_id.py <建文档响应文件>
```

输出 `document_id`（兼容 document.id / documents[0].id / data[0].id 三种形态）。

### 第 6 步：LLM 判断 + 构造打标 payload + 打标

```bash
python Scripts/build_metadata.py <llm输出文件> <document_id> <version> <mineru_version_id> <mineru_file_role_id> <mineru_doc_summary_id> <mineru_doc_type_id>
```

- 先把文档内容片段（第 3 步 cleaned.md 前若干段）交给 LLM，按 kb-tagger 的 7 分类法输出 `{"file_role": "...", "doc_summary": "15字内", "doc_type": "..."}`
- build_metadata.py 构造 payload → 调 `POST /v1/datasets/{mineru_dataset_id}/documents/metadata` 打标
- `document_id` 为空（xlsx 跳过 MinerU 链）→ 输出空 payload，接口空操作，不报错

### 第 7 步：MinIO 入桶 + 索引同步

```bash
python Scripts/minio_client.py list
python Scripts/update_index.py <索引文件> <version> <file_name>
python Scripts/minio_client.py put "<version>/<file_name>.md" <cleaned.md 内容>
python Scripts/minio_client.py put "_index.json" <update_index 输出的 index_json>
```

- 入桶对象名 = `{version}/{file_name}.md`（diff-expert 定位就靠这个命名规范）
- 索引追加 `{file_name}.md` 并**排序**（保证 diff-expert 匹配平局的确定性）
- 索引不存在 → 从空清单重建

## 交付物

- 入库结果汇总：文件名、version、路由到的库（老库/MinerU 库）、document_id、打标结果、MinIO 对象名与索引更新状态
- 打标与 MinIO 操作都要给接口返回状态（成功/失败+原因）

## 参考

- `Reference/入库全流程.md`：全链路说明、MinerU 库字段 ID、已知坑（xlsx 分流、create-by-text 不带 metadata、md_cleaner 日志污染、凭据空格、节点变量引用）
- `Scripts/`：ingest_cfg.py / create_by_text.py / extract_doc_id.py / build_metadata.py / update_index.py / minio_client.py（全部标准库，无第三方依赖）

## 注意

- 脚本在技能目录下执行，cwd 已在技能包根目录（`python Scripts/xxx.py`）
- MinIO 凭据在 minio_client.py 默认值（minioadmin/minioadmin123，桶 dify-files），环境变量可覆盖
- Dify API 默认 `http://127.0.0.1/v1`，key `dataset-Kz491fr3x8jSWR8QEC8BYG3Z`，环境变量可覆盖
- 不要修改脚本本身；字段 ID 以 ingest_cfg.py 输出为准
