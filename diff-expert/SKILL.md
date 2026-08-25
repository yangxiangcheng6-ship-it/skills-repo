---
name: diff-expert
description: 文档差异对比专家。对比「标准版」与「偏离版」两份合同/协议文档（含 Master Agreement、Framework Agreement、Appendix A/B/C/D/E/F 全套，数据源 MinIO 桶 dify-files）。当用户要对比两个版本差异、查偏离了哪些条款、看偏离版改了什么、输出差异表/对比报告时使用。不适合：单文档问答、非标准/偏离对比的通用问答。
---

# 文档差异对比专家（diff-expert）

对比标准版与偏离版文档，输出结构化差异表。机械步骤（定位/读取/diff）由脚本完成，判断步骤（分类/提炼）由 LLM 完成。

## 何时触发

- 用户要求对比同一文档的标准版/偏离版差异："对比一下"、"偏离了哪些"、"改了什么"、"差异表"、"差异报告"
- 用户给出文档主题（如 "Appendix A"、"主协议"、"数据处理协议"、"报价单"）

**话题过滤（第一道门槛）**：只处理"标准版 vs 偏离版文档差异"类问题。单文档问答、知识库检索类问题、无明确版本对比意图的问题，直接说明不适用并建议换技能。

## 执行流程（严格按顺序）

### 第 1 步：提取参数
必须拿到：文档主题 `topic`（如 Appendix A / 主协议 / 数据处理协议 / 报价单）。
用户没给 topic 时追问；给的 topic 含糊时先追问澄清，不猜。

### 第 2 步：定位文档
```bash
python Scripts/find_docs.py "<topic>"
```
输出 JSON：`matched`、`standard.filename`、`deviation.filename`。
- `matched: false` 时：读 `hint` 和 `alternatives`，把候选文件名回给用户确认后再继续，**不要硬猜**。

### 第 3 步：分块对比
```bash
python Scripts/diff_docs.py "<标准版文件名>" "<偏离版文件名>" > diff_result.json
```
输出差异块 JSON（`stats` + `blocks`，每块 type=replace/delete/insert，含行号与两侧内容）。

### 第 4 步：LLM 提炼差异表
```bash
python Scripts/summarize_prompt.py --file diff_result.json [--compact]
```
生成提炼模板（硬规则在模板里）：输出 JSON 数组，每项 {条款, 变化类型, 标准版内容, 偏离版内容, 实质影响}。
- `--compact`：差异块 ≤ 10 时用，把全部差异块拼进 prompt 一次提炼
- 差异块 > 10：分批喂给 LLM（每批 ≤ 10 块），最后合并去重
- 把模板喂给当前 LLM，得到差异表；**只报实质差异**（忽略清洗统计头/版本戳/水印/纯空白差异）

### 第 5 步：输出报告
- 差异表 + 汇总统计（差异块数、涉及条款数、变化类型分布）
- 按"影响程度"排序：义务加重/减轻、责任转移、范围变化等实质差异放前面
- 找不到对应条款号的差异标"无明确条款号"

## 交付物

- 结构化差异表（JSON 数组或 markdown 表格，按用户偏好）
- 差异统计一行总结
- 原始差异块文件 `diff_result.json`（如需溯源，标记交付）

## 参考

- `Reference/对比链方法.md`：方法论详解（分类过滤、topic 匹配、sanitize 残留、截断、评测教训）
- `Scripts/`：minio_client.py / find_docs.py / diff_docs.py / summarize_prompt.py（全部标准库，无第三方依赖）

## 注意

- 脚本在技能目录下执行，cwd 已在技能包根目录（`python Scripts/xxx.py`）
- MinIO 凭据在 minio_client.py 默认值，环境变量可覆盖
- 索引 `_index.json` 记录标准/偏离两侧文件名清单；文档是已清洗的 .docx.md（含清洗统计头，提炼时忽略）
- 不要修改脚本本身；topic 匹配结果以 find_docs.py 输出为准
