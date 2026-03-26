# 视觉伴随使用指南

这是一个基于浏览器的 brainstorming 视觉辅助工具，用来展示草图、图表和多个可选方案。

## 什么时候用

按“每个问题”判断，不按“整个会话”判断。标准只有一个：**用户看见它，会不会比读文字更容易理解？**

**使用浏览器**，当内容本身是视觉性的：

- **UI 草图**：线框图、布局、导航结构、组件设计
- **架构图**：系统组件、数据流、关系图
- **并排视觉对比**：比较两个布局、两套配色、两种设计方向
- **设计打磨**：当问题聚焦于观感、留白、视觉层级
- **空间关系**：状态机、流程图、实体关系图

**使用终端**，当内容本身是文本或表格：

- **需求和范围问题**：例如“X 是什么意思？”“哪些功能要纳入范围？”
- **概念性 A/B/C 选择**：方案主要靠文字描述即可比较
- **取舍列表**：优缺点、对比表
- **技术决策**：API 设计、数据建模、架构方案选择
- **澄清问题**：凡是回答重点在文字而不是视觉偏好的问题

一个问题“关于 UI”并不自动等于“应该用浏览器”。“你想要什么类型的向导流程？”是概念问题，用终端；“这两种向导布局哪种更顺手？”才是视觉问题，用浏览器。

## 工作方式

服务端会监听一个目录中的 HTML 文件，并把最新文件渲染到浏览器。你写 HTML 内容，用户在浏览器中查看并点击选择；这些选择会记录到 `.events` 文件，供你下一轮读取。

**内容片段 vs 完整文档：** 如果 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务端会按原样提供（只注入辅助脚本）。否则，服务端会自动把内容包进框架模板，补上页头、CSS 主题、选择状态栏和交互基础设施。**默认写内容片段。** 只有在确实需要完全控制页面时，才写完整 HTML 文档。

## 启动会话

```bash
# 启动服务，并将会话内容持久化到项目目录
scripts/start-server.sh --project-dir /path/to/project

# 返回：
# {"type":"server-started","port":52341,"url":"http://localhost:52341",
#  "screen_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000"}
```

保存返回值里的 `screen_dir`。然后告诉用户打开该 URL。

**如何找到连接信息：** 服务启动后会把启动 JSON 写入 `$SCREEN_DIR/.server-info`。如果你是后台启动、没有直接拿到 stdout，就读这个文件拿 URL 和端口。使用 `--project-dir` 时，也可以去 `<project>/.superpowers/brainstorm/` 下查会话目录。

**注意：** 请把项目根目录传给 `--project-dir`，这样草图会保存在 `.superpowers/brainstorm/` 下，服务重启后仍然存在。不传时，文件会写到 `/tmp`，后续可能被清理。若项目还没忽略 `.superpowers/`，记得提醒用户加入 `.gitignore`。

**不同平台的启动方式：**

**Claude Code（macOS / Linux）：**
```bash
# 默认模式即可，脚本会自行把服务放到后台
scripts/start-server.sh --project-dir /path/to/project
```

**Claude Code（Windows）：**
```bash
# Windows 会自动切到前台模式，此命令会阻塞工具调用。
# 通过 Bash 工具调用时，应设置 run_in_background: true，
# 然后下一轮再去读 $SCREEN_DIR/.server-info
scripts/start-server.sh --project-dir /path/to/project
```

**Codex：**
```bash
# Codex 会回收后台进程。脚本会自动检测 CODEX_CI 并切到前台模式。
# 直接正常运行即可，不需要额外参数。
scripts/start-server.sh --project-dir /path/to/project
```

**Gemini CLI：**
```bash
# 使用 --foreground，并在 shell 工具调用时设置 is_background: true
scripts/start-server.sh --project-dir /path/to/project --foreground
```

**其他环境：** 这个服务需要在多个对话回合之间持续存活。如果你的环境会回收脱离终端的后台进程，就使用 `--foreground`，并配合所在平台支持的后台运行方式。

如果浏览器无法访问这个 URL（远程/容器环境里很常见），改成绑定非回环地址：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

用 `--url-host` 控制返回 JSON 里展示的主机名。

## 交互循环

1. **确认服务仍然活着**，然后**向 `screen_dir` 写入新的 HTML 文件**：
   - 每次写之前，先检查 `$SCREEN_DIR/.server-info` 是否存在。如果不存在，或者 `.server-stopped` 已出现，说明服务已经退出，需要先重新执行 `start-server.sh`
   - 服务在空闲 30 分钟后会自动退出
   - 使用有语义的文件名，例如 `platform.html`、`visual-style.html`、`layout.html`
   - **不要复用旧文件名**，每个画面都用一个新文件
   - 用写文件工具，**不要用 `cat` 或 heredoc**
   - 服务会自动渲染最新的 HTML 文件

2. **告诉用户接下来会看到什么，然后结束这一轮：**
   - 每一步都重复告知 URL，不要只在第一次说
   - 用一句简短文字描述当前画面，例如“现在展示的是首页的 3 种布局方向”
   - 请用户在终端回复：“你先看一下，觉得哪个方向更合适就告诉我；如果你愿意，也可以直接点选。”

3. **下一轮轮到你时**，也就是用户已经在终端回复后：
   - 读取 `$SCREEN_DIR/.events`（如果存在），里面是浏览器交互记录的 JSON Lines
   - 把这些结构化交互数据和用户在终端中的文字反馈合并理解
   - 终端消息仍然是主反馈来源；`.events` 只是补充结构化信息

4. **迭代或推进**：
   - 如果反馈要求修改当前画面，就写一个新文件，例如 `layout-v2.html`
   - 只有当前步骤已经被确认后，才进入下一个问题

5. **回到终端时，推送等待页清空旧画面**：

   ```html
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">接下来转到终端继续沟通……</p>
   </div>
   ```

   这样可以避免用户还盯着一个已经讨论完的旧画面。下一个需要视觉内容的问题出现时，再推送新的 HTML 文件。

6. 重复以上流程，直到结束。

## 如何写内容片段

只写页面主体内容即可。服务会自动套上框架模板，包括页头、主题样式、选择状态栏和交互逻辑。

**最小示例：**

```html
<h2>你觉得哪种布局更合适？</h2>
<p class="subtitle">重点看可读性和视觉层级</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>单栏布局</h3>
      <p>阅读更聚焦，页面更干净</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>双栏布局</h3>
      <p>左侧导航配合右侧主内容</p>
    </div>
  </div>
</div>
```

就这些。不需要写 `<html>`、CSS 或 `<script>`。服务端会自动补齐。

## 可用 CSS 类

框架模板预置了以下 CSS 类，供你的内容直接使用：

### 选项卡（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>标题</h3>
      <p>说明</p>
    </div>
  </div>
</div>
```

**多选：** 在容器上加 `data-multiselect`，即可允许用户多选。每次点击都会切换选中状态，底部提示栏会显示选中数量。

```html
<div class="options" data-multiselect>
  <!-- 结构不变，用户可以选中或取消多个选项 -->
</div>
```

### 卡片（展示视觉方案）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- 视觉内容 --></div>
    <div class="card-body">
      <h3>方案名</h3>
      <p>方案说明</p>
    </div>
  </div>
</div>
```

### 模拟稿容器

```html
<div class="mockup">
  <div class="mockup-header">预览：仪表盘布局</div>
  <div class="mockup-body"><!-- 你的模拟稿 HTML --></div>
</div>
```

### 分栏对比（左右并排）

```html
<div class="split">
  <div class="mockup"><!-- 左侧 --></div>
  <div class="mockup"><!-- 右侧 --></div>
</div>
```

### 优缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>优点</h4><ul><li>好处</li></ul></div>
  <div class="cons"><h4>缺点</h4><ul><li>代价</li></ul></div>
</div>
```

### 模拟元素（线框图基础积木）

```html
<div class="mock-nav">Logo | 首页 | 关于 | 联系我们</div>
<div style="display: flex;">
  <div class="mock-sidebar">导航区</div>
  <div class="mock-content">主内容区</div>
</div>
<button class="mock-button">操作按钮</button>
<input class="mock-input" placeholder="输入框">
<div class="placeholder">占位区域</div>
```

### 排版与分区

- `h2`：页面标题
- `h3`：区块标题
- `.subtitle`：副标题或补充说明
- `.section`：逻辑分组
- `.label`：小型标签
