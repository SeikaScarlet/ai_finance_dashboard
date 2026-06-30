# 📦 资产看板 · 部署与使用指南

> **项目特点：** 纯静态 Web 应用，无需数据库/后端，运行在浏览器本地

---

## 📋 目录

- [一、系统要求](#一系统要求)
- [二、快速开始（5 分钟）](#二快速开始5-分钟)
- [三、三种部署方式](#三三种部署方式)
- [四、初次配置](#四初次配置)
- [五、日常使用](#五日常使用)
- [六、安全与备份](#六安全与备份)
- [七、常见问题](#七常见问题)

---

## 一、系统要求

### 必需（运行看板）

| 组件 | 版本 | 用途 |
|---|---|---|
| **浏览器** | Chrome 90+ / Safari 14+ / Firefox 88+ | 运行看板 UI |
| **HTTP 服务器** | 任意 | 本地预览（避免 CORS 限制） |

### 可选（辅助脚本）

| 组件 | 版本 | 用途 |
|---|---|---|
| **Python** | 3.7+ | 抓汇率、报数助手、数据验证 |
| **Git** | 2.0+ | 版本控制（推荐） |

### 推荐配置

- **操作系统：** macOS / Windows / Linux 均可
- **磁盘空间：** < 10 MB（纯代码） + 数据文件（通常 < 1 MB）
- **内存：** 无特殊要求（浏览器即可）

---

## 二、快速开始（5 分钟）

### 方式 A：直接打开演示（体验功能）

```bash
# 1. 下载项目
git clone https://github.com/YOUR_USERNAME/asset_dashboard.git
cd asset_dashboard

# 2. 启动本地服务器
python3 -m http.server 8765
# 或者（如果没有 Python）：
# npx serve .
# php -S localhost:8765

# 3. 浏览器打开
open http://localhost:8765
# 或手动访问：http://127.0.0.1:8765
```

**效果：** 立即看到演示数据（`demo_data/`），所有功能可用。

---

### 方式 B：使用真实数据（完整部署）

```bash
# 1. 创建数据目录
mkdir -p data
mkdir -p data/transactions/yearly
mkdir -p data/_backups

# 2. 复制演示数据作为模板（脱敏后修改）
cp -r demo_data/* data/

# 3. 创建配置文件
cat > config.js << 'EOF'
window.AFD_CONFIG = {
  dataDir: "data"  // 改为使用真实数据
};
EOF

# 4. 启动服务
python3 -m http.server 8765

# 5. 浏览器打开
open http://localhost:8765
```

**重要：** 修改 `data/` 中的所有金额为你的真实数据。

---

## 三、三种部署方式

### 部署 1：本地预览（推荐）⭐⭐⭐⭐⭐

**适合：** 个人使用、数据敏感、最安全

**步骤：**

```bash
# 克隆项目到本地
cd ~/Documents  # 或你的工作目录
git clone https://github.com/YOUR_USERNAME/asset_dashboard.git
cd asset_dashboard

# 启动服务（三选一）
python3 -m http.server 8765           # Python 3
python2 -m SimpleHTTPServer 8765      # Python 2
npx serve . -p 8765                   # Node.js

# 访问
http://localhost:8765
```

**优点：**
- ✅ 数据不出本地
- ✅ 无需配置域名/证书
- ✅ 启动即用

**缺点：**
- ❌ 需要电脑开机
- ❌ 手机无法访问（除非同一 WiFi）

---

### 部署 2：家庭内网（局域网访问）⭐⭐⭐⭐

**适合：** 家庭多设备访问、iPhone/iPad 随时查看

**步骤：**

```bash
# 1. 在家中主力电脑（Mac/PC）部署
cd ~/asset_dashboard

# 2. 绑定到所有网卡（允许局域网访问）
python3 -m http.server 8765 --bind 0.0.0.0

# 3. 查看本机 IP
# macOS:
ipconfig getifaddr en0  # 例如 192.168.1.100

# Windows:
ipconfig | findstr IPv4  # 例如 192.168.1.100

# Linux:
ip addr show | grep "inet "

# 4. 手机/iPad 浏览器访问
http://192.168.1.100:8765
```

**优点：**
- ✅ 家中任意设备可访问
- ✅ 数据仍在本地
- ✅ iPhone Safari 体验良好

**缺点：**
- ❌ 只能在家中 WiFi 下访问
- ❌ 电脑需要常开

**进阶：使用 Tailscale（外网也能访问）**

```bash
# 1. 安装 Tailscale（免费 VPN）
# macOS: brew install tailscale
# 或访问 https://tailscale.com/download

# 2. 启动
sudo tailscale up

# 3. 获取 Tailscale IP（例如 100.x.x.x）
tailscale ip

# 4. iPhone 安装 Tailscale App 并登录
# 5. 任何地方都可以通过 http://100.x.x.x:8765 访问
```

---

### 部署 3：私有云端（Cloudflare Pages / Vercel）⭐⭐

**⚠️ 警告：** 仅用于**演示数据**，不要上传真实 `data/`！

**适合：** 公开展示、团队协作（使用脱敏数据）

**步骤（Vercel）：**

```bash
# 1. 确保 .gitignore 屏蔽了 data/
cat .gitignore | grep "^data/"  # 应该有这一行

# 2. 提交代码到 GitHub（data/ 不会被上传）
git add .
git commit -m "Deploy to Vercel"
git push origin main

# 3. 访问 vercel.com，导入 GitHub 仓库
# 4. 自动部署，获得 https://your-project.vercel.app
```

**优点：**
- ✅ 全球 CDN 加速
- ✅ HTTPS 自动配置
- ✅ 无需服务器维护

**缺点：**
- ❌ 数据公开（除非付费私有部署）
- ❌ 仅适合演示

---

## 四、初次配置

### 步骤 1：创建真实数据目录

```bash
cd asset_dashboard

# 创建目录结构
mkdir -p data/transactions/yearly
mkdir -p data/_backups

# 复制演示数据作为模板
cp demo_data/target.json data/
cp demo_data/history.json data/
cp demo_data/recurring.json data/
cp demo_data/liabilities.json data/
cp demo_data/policies.json data/
cp demo_data/categories.json data/
cp demo_data/income_events.json data/
cp demo_data/risks.json data/
cp demo_data/transactions/index.json data/transactions/
```

---

### 步骤 2：配置数据源

**方式 A：通过 config.js（推荐）**

```bash
cat > config.js << 'EOF'
window.AFD_CONFIG = {
  dataDir: "data"  // 使用真实数据（不上 Git）
  // dataDir: "demo_data"  // 切换回演示数据
};
EOF
```

**方式 B：通过 UI 切换（运行时）**

打开看板 → 右上角 **数据：DEMO** 下拉框 → 选择 **私有**

---

### 步骤 3：脱敏并填写真实数据

#### 3.1 修改 `data/target.json`（终局目标）

```bash
vim data/target.json  # 或用 VS Code 打开

# 需要改的字段：
{
  "retirement": {
    "selfRetireYear": 2027,          # ← 你的退休年份
    "wifeRetireYear": 2027,
    "selfSalaryAnnual": 540000,      # ← 你的年薪
    "wifeSalaryAnnual": 216000       # ← 配偶年薪
  },
  "redLines": {
    "rmbMaxPct": 0.70               # ← RMB 占比红线（70%）
  },
  "modules": [
    # 调整四大类的目标占比
    {"key": "defense", "targetPct": 0.16},     # 防御现金 16%
    {"key": "cashflow", "targetPct": 0.66},    # 稳健现金流 66%
    {"key": "growth", "targetPct": 0.10},      # 全球增长 10%
    {"key": "hedge", "targetPct": 0.08}        # 避险卫星 8%
  ]
}
```

#### 3.2 填写首次快照 `data/history.json`

```bash
# 1. 抓实时汇率
python3 scripts/fetch_rates.py --json

# 2. 复制输出，替换 history.json 的第一条 snapshot

# 3. 手动填写你的持仓
{
  "snapshots": [
    {
      "date": "2026-06-30",
      "rates": {"USD": 6.80, "HKD": 0.87},
      "comment": "首次建档",
      "holdings": {
        "weizhong_demand": {"raw": 50000},        # 微众活期 5 万
        "voo": {"shares": 30, "cost": 520.0}      # VOO 30 股
      }
    }
  ]
}
```

#### 3.3 配置循环收支 `data/recurring.json`

```json
{
  "incomes": [
    {
      "key": "salary_self",
      "name": "工资 · Self",
      "ccy": "RMB",
      "amount": 22000,        # ← 你的月薪（税后）
      "frequency": "monthly"
    }
  ],
  "expenses": [
    {
      "key": "car_insurance",
      "name": "车险",
      "ccy": "RMB",
      "amount": 4000,         # ← 年度车险
      "frequency": "annual"
    }
  ]
}
```

---

### 步骤 4：验证配置

```bash
# 1. 验证所有 JSON 格式正确
python3 -c "
import json
files = [
  'data/target.json',
  'data/history.json',
  'data/recurring.json',
  'data/liabilities.json'
]
for f in files:
  json.load(open(f))
  print(f'✅ {f}')
print('✅ 所有文件格式正确')
"

# 2. 启动看板
python3 -m http.server 8765

# 3. 浏览器打开 http://localhost:8765
# 检查：
# - 顶部 KPI 是否显示了你的数据
# - 健康检查 banner 是否有红色告警
# - 控制台（F12）是否有报错
```

---

## 五、日常使用

### 5.1 每月/季度报数（更新资产快照）

```bash
cd asset_dashboard

# Step 1: 备份（必须！）
python3 scripts/backup_data.py "2026-06 月度报数"

# Step 2: 交互式更新 holdings
python3 scripts/update_holdings.py
# 按提示逐项确认变动

# Step 3: 或使用自动化脚本
python3 scripts/auto_snapshot.py

# Step 4: 复制输出的 JSON，append 到 data/history.json

# Step 5: 验证
python3 -m http.server 8765
# 浏览器刷新看板
```

---

### 5.2 修改战略目标

```bash
# Step 1: 备份
python3 scripts/backup_data.py "调整 RMB 红线到 65%"

# Step 2: 编辑 target.json
vim data/target.json

# Step 3: 在 changelog 里记录变更
{
  "changelog": [
    {
      "version": "2.2",
      "date": "2026-06-30",
      "changes": [
        "RMB 红线从 70% 调整到 65%"
      ]
    }
  ]
}

# Step 4: 验证
python3 -m http.server 8765
```

---

### 5.3 导入年度账单（现金流 Tab）

```bash
# Step 1: 准备 CSV（从支付宝/招行/随手记导出）
# 格式要求：年份,类目,名称,谁,金额

# Step 2: 转换为 JSON
# （手动整理到 data/transactions/yearly/2026.json）

# 示例：
{
  "year": "2026",
  "status": "complete",
  "expenses": [
    {"category": "food", "name": "食品酒水", "amount": 8200, "ccy": "RMB", "by": "joint"}
  ]
}

# Step 3: 更新索引
vim data/transactions/index.json
# 添加 "2026" 到 years 数组

# Step 4: 刷新看板，切换到现金流 Tab
```

---

### 5.4 定期再平衡（季度末）

```bash
# Step 1: 打开看板，查看偏离告警
http://localhost:8765

# Step 2: 查看 "偏离告警 · Sub 项明细" 表格
# 识别超标/偏低的资产

# Step 3: 执行交易（券商 App）
# 例如：
# - RMB 超标 → 买入美元资产
# - 腾讯超红线 → 执行减仓阶梯

# Step 4: 报数（记录交易后的新持仓）
python3 scripts/update_holdings.py

# Step 5: 填写 comment
"Q2 再平衡：卖腾讯 30 万 RMB → 加仓 VOO"
```

---

## 六、安全与备份

### 6.1 本地备份（自动）

```bash
# 每次改 data/ 之前自动备份
python3 scripts/backup_data.py "改动说明"

# 备份位置：data/_backups/<时间戳>/
# 保留最近 20 份，自动删除旧备份

# 恢复备份：
cp -r data/_backups/2026-06-30-140522/* data/
```

---

### 6.2 云端备份（推荐）

**方式 A：iCloud / OneDrive / Dropbox**

```bash
# 1. 把整个项目文件夹放到云盘目录
mv asset_dashboard ~/iCloud/
# 或
mv asset_dashboard ~/OneDrive/

# 2. 自动同步（无需额外操作）
# data/ 会实时备份到云端
```

**方式 B：私有 Git 仓库（加密）**

```bash
# ⚠️ 注意：必须是私有仓库 + 加密

# 1. 使用 git-crypt 加密 data/
brew install git-crypt
cd asset_dashboard
git-crypt init

# 2. 配置加密规则
cat > .gitattributes << 'EOF'
data/** filter=git-crypt diff=git-crypt
EOF

# 3. 添加密钥（保存到安全位置）
git-crypt add-gpg-user YOUR_GPG_KEY

# 4. 正常提交（data/ 会被自动加密）
git add data/
git commit -m "Add encrypted data"
git push origin main
```

---

### 6.3 安全检查清单

- [ ] `data/` 已被 `.gitignore` 屏蔽
- [ ] 从未将 `data/` 提交到公开 GitHub
- [ ] 截图时开启了隐私模式（隐藏金额）
- [ ] 定期备份到云端（加密）
- [ ] 使用强密码保护云端账号（双因素认证）

---

## 七、常见问题

### Q1: 浏览器打开白屏 / 控制台报 CORS 错误

**原因：** 直接用 `file://` 协议打开 HTML，浏览器拦截了 `fetch` 请求。

**解决：**
```bash
# 必须通过 HTTP 服务器访问
python3 -m http.server 8765
# 然后打开 http://localhost:8765
```

---

### Q2: 数据不显示 / 显示 "暂无数据"

**原因：** 数据源配置错误或 JSON 格式有误。

**排查：**
```bash
# 1. 检查数据源
cat config.js  # 应该是 dataDir: "data"

# 2. 验证 JSON 格式
python3 -c "import json; json.load(open('data/history.json'))"
# 如果报错，说明 JSON 格式不正确

# 3. 浏览器控制台（F12）查看错误
```

---

### Q3: iPhone Safari 字体太小 / 布局错乱

**解决：**
```bash
# 项目已适配移动端，确保：
# 1. 用最新版 Safari（iOS 14+）
# 2. 清除浏览器缓存
# 3. 硬刷新（下拉页面释放）
```

---

### Q4: 如何在多台设备间同步数据？

**方式 A：云盘同步（推荐）**
- 把整个项目放到 iCloud / OneDrive
- 所有设备自动同步

**方式 B：Git 同步（手动）**
```bash
# 设备 A 改完后：
git add data/
git commit -m "Update holdings"
git push origin main

# 设备 B 拉取：
git pull origin main
```

---

### Q5: 如何分享给配偶/家人查看？

**方式 A：局域网访问（推荐）**
```bash
# 主力电脑启动服务
python3 -m http.server 8765 --bind 0.0.0.0

# 家人手机/iPad 浏览器访问
http://192.168.1.100:8765  # 换成你的电脑 IP
```

**方式 B：Tailscale（外网也能访问）**
- 主力电脑安装 Tailscale
- 家人设备也装 Tailscale 并登录同一账号
- 通过 `http://100.x.x.x:8765` 访问

---

### Q6: Python 脚本报错 `ModuleNotFoundError`

**原因：** 缺少依赖（但项目只用标准库，不应该缺）

**检查：**
```bash
python3 --version  # 确保 3.7+

# 脚本只依赖标准库：
# - json, sys, urllib, datetime, pathlib
# 无需 pip install 任何东西
```

---

### Q7: 数据文件被误删了怎么办？

**恢复：**
```bash
# 方式 1：从自动备份恢复
ls data/_backups/  # 列出所有备份
cp -r data/_backups/2026-06-30-140522/* data/

# 方式 2：从云盘恢复
# iCloud / OneDrive 通常有版本历史

# 方式 3：从 Git 历史恢复（如果有加密提交）
git checkout HEAD^ -- data/
```

---

### Q8: 如何导出 PDF 报告？

**浏览器打印：**
```bash
# 1. 打开看板
# 2. 隐藏金额（点击右上角"隐藏金额"按钮）
# 3. Cmd+P（macOS）或 Ctrl+P（Windows）
# 4. 另存为 PDF
```

**高级：使用 Puppeteer 截图**
```bash
node scripts/take_screenshots.mjs
# 输出到 screenshots/ 文件夹
```

---

## 八、升级项目

### 从上游仓库拉取更新

```bash
# 1. 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_AUTHOR/asset_dashboard.git

# 2. 拉取最新代码
git fetch upstream
git merge upstream/main

# 3. 解决冲突（如果有）
# 通常只有 JS/HTML 会更新，data/ 不会冲突

# 4. 测试
python3 -m http.server 8765
```

---

## 九、性能优化

### 9.1 history.json 太大（> 100 条快照）

**方案：分档压缩**

```bash
# 1. 将 2024 年的快照移到单独文件
vim data/history_archive_2024.json

# 2. 在 history.json 保留最近 2 年
# 3. 看板会自动忽略旧快照
```

---

### 9.2 离线化外部资源（无网络环境）

```bash
# 1. 下载 ECharts
wget https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js

# 2. 修改 index.html
sed -i '' 's|https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js|./echarts.min.js|' index.html

# 3. （可选）下载字体到本地
# 或改为系统字体
```

---

## 十、技术支持

### 社区资源

- **GitHub Issues:** https://github.com/YOUR_USERNAME/asset_dashboard/issues
- **讨论区:** GitHub Discussions
- **文档:** README.md / AGENTS.md / DEPLOYMENT.md

### 反馈与贡献

```bash
# 发现 Bug
1. 截图 + 控制台错误日志
2. 提交 Issue 到 GitHub

# 功能建议
1. 在 Discussions 发起讨论
2. 等待社区反馈

# 贡献代码
1. Fork 仓库
2. 创建 feature 分支
3. 提交 Pull Request
```

---

## 附录：命令速查表

### 日常操作

```bash
# 启动服务
python3 -m http.server 8765

# 备份数据
python3 scripts/backup_data.py "改动说明"

# 抓汇率
python3 scripts/fetch_rates.py --json

# 交互式报数
python3 scripts/update_holdings.py

# 验证 JSON
python3 -c "import json; json.load(open('data/history.json')); print('OK')"

# 查看备份列表
ls -lh data/_backups/

# 恢复备份
cp -r data/_backups/2026-06-30-140522/* data/
```

### Git 操作

```bash
# 查看状态（data/ 不应出现）
git status

# 提交代码（不含 data/）
git add .
git commit -m "Update dashboard UI"
git push origin main

# 拉取更新
git pull origin main
```

---

## 结语

**核心原则：**
1. **数据安全第一** — `data/` 绝不上传
2. **定期备份** — 每次改动前先备份
3. **版本控制** — 代码用 Git，数据用云盘
4. **简单至上** — 纯静态，无需复杂配置

**祝你使用愉快！** 🎉
