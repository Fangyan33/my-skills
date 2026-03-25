---
name: gen-docx
description: 当用户要求把 Markdown 文档转换为 Word 文档、生成 `.docx`、还原 simple.docx 模板样式、使用 python-docx 控制页面/字体/段落/编号/页眉页脚，或讨论公文/汇报材料版式规范时使用。本 skill 提供 Markdown 到 DOCX 的可复用脚本、Word 排版约束、降级策略和自检流程。
---

# gen-docx

这个 skill 用于把 Markdown 稳定转换为符合本项目规范的 `.docx` 文档。
默认优先调用脚本，而不是每次临时重写 `python-docx` 代码。

## 执行顺序

1. 先阅读 `references/style-spec.md`
2. 优先使用 `scripts/md_to_docx.py`
3. 只有当脚本无法覆盖需求时，才补写或修改 `python-docx` 代码
4. 明确说明脚本直出部分与降级部分

## 脚本用法

```bash
python3 scripts/md_to_docx.py input.md output.docx
```

可选参数：

- `--title "自定义标题"`：覆盖从 Markdown 读取到的标题
- `--footer "页脚文本"`：写入页脚
- `--author "作者"`：写入文档元数据
- `--subject "主题"`：写入文档元数据

## Markdown 映射规则

- `# 标题`：映射为主标题；默认只取第一个一级标题作为文档标题
- `## 标题`：映射为一级标题
- `### 标题`：映射为二级标题
- 普通段落：映射为正文段落
- `- item` / `* item` / `1. item`：映射为文本列表项，不依赖自动编号
- `**加粗**`：映射为粗体
- `==高亮==`：映射为黄色高亮
- 空行：分隔段落

脚本当前定位是稳定处理常见公文/汇报 Markdown 子集，不追求完整 Markdown 规范。
遇到表格、图片、代码块、嵌套列表、引用块等复杂结构时，优先降级为普通段落文本，并在命令行输出中打印 warning。

## 处理优先级

1. 用户明确要求
2. `references/style-spec.md`
3. 脚本默认行为
4. 其他临时实现

## 参考资料

完整规范见：`references/style-spec.md`。

使用时应把该参考文件视为本 skill 的正式约束来源，包括：
- 页面与页边距
- 标题/正文/列表项样式
- 页眉页脚
- 编号规则
- 高亮与固定行距
- 字体回退
- 降级策略
- 输出检查清单
- `python-docx` 概念映射
