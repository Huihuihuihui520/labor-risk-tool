# 移动端Bug修复验证指南

## 快速开始

### 立即测试（在云端部署后）

使用以下URL在手机上测试：
```
https://your-deployed-domain.com
```

---

## 功能验证清单

### ✅ 1. Viewport与缩放
**步骤：**
1. 在iPhone上打开应用
2. 用双指做捏合动作（放大/缩小）
3. **预期**：页面可正常缩放（在20-500%之间）

**验证命令：** 检查index.html第2-3行
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<!-- 不应该有 maximum-scale=1.0 或 user-scalable=no -->
```

---

### ✅ 2. 刘海屏适配（iPhone X/11/12+）
**步骤：**
1. 在iPhone X或更新机型上打开
2. 查看底部"开始分析"按钮
3. **预期**：按钮完全可见，不被Home Indicator遮挡

**Chrome开发者工具验证：**
```javascript
// 在Console中运行
const app = document.getElementById('app')
console.log('安全区右边距:', getComputedStyle(app).paddingRight)
console.log('安全区底部距离:', getComputedStyle(app).paddingBottom)
```

---

### ✅ 3. 布局稳定性（100vh问题）
**步骤：**
1. 用Safari在iPhone上打开
2. 向下滚动到底部按钮
3. 向上滚动（地址栏消失）
4. **预期**：页面流畅，无闪烁/跳跃

**开发者工具检查：**
```css
/* 验证CSS中是否使用了100dvh */
#app {
    height: 100dvh;  /* ✓ 正确 */
    /* height: 100vh; */ /* ✗ 错误 */
}
```

---

### ✅ 4. 流式响应（AI分析）
**步骤：**
1. 设置API Key
2. 填写基本产程信息
3. 点击"开始专家评估"
4. **预期**：文本逐字流式显示，而不是一次性加载

**浏览器Network检查：**
- 请求URL：`/api/analyze/stream`
- Content-Type：`text/event-stream`
- 状态码：`200 OK`
- Transfer-Encoding：`chunked` ✓

---

### ✅ 5. localStorage降级
**步骤（iPhone无痕模式）：**
1. Safari → 文件 → 新建无痕标签页
2. 打开应用，配置API Key
3. 点击"保存配置"
4. 刷新页面
5. **预期**：显示提示，但不崩溃；功能正常

**Console验证：**
```javascript
// 无痕模式下运行
try {
    localStorage.setItem('test', 'value')
    console.log('✓ localStorage可用')
} catch(e) {
    console.warn('⚠️ localStorage不可用（无痕模式）')
}
```

---

### ✅ 6. 小屏幕适配（320px）
**步骤：**
1. Chrome DevTools → 设备模式
2. 选择"iPhone SE 2"（375px）或自定义320px
3. 检查所有元素显示
4. **预期**：没有水平滚动条，文本清晰

**关键尺寸检查：**
- 卡片边距：≥12px
- 字体大小：≥13px（body文本）
- 按钮高度：≥44px（触摸目标）
- 输入框高度：≥40px

---

### ✅ 7. 响应式仪表板
**步骤：**
1. 竖屏：验证PPH指标卡片对齐
2. 横屏：验证模态框宽度
3. **预期**：布局自适应，无内容溢出

```css
/* 验证响应式规则 */
@media(max-width:384px) {
    .rc-info p.text-base { font-size: 0.875rem }  /* ✓ 存在 */
}
```

---

### ✅ 8. 输入框体验
**步骤：**
1. 手机上点击"孕周"输入框
2. 虚拟键盘弹起
3. **预期**：
   - 输入框保持可见
   - 内容不被键盘遮挡
   - 能向上滚动查看顶部

**验证输入框配置：**
```html
<input type="number" 
       style="font-size: 16px !important;"  
       required>
```

---

### ✅ 9. 弹窗显示
**步骤：**
1. 输入危险指标（如胎心率<110）
2. 点击"开始评估"
3. **预期**：红色警报弹窗出现在屏幕中央
   - 不被底部按钮遮挡
   - 可正常点击"我已知晓"关闭

**z-index验证：**
```html
<!-- 临界弹窗应使用 z-50 或更高 -->
<div class="fixed inset-0 z-50 bg-black/70">
```

---

### ✅ 10. 网络切换
**步骤（iOS上）：**
1. WiFi连接，开始分析
2. 分析过程中关闭WiFi，用4G继续
3. **预期**：请求自动重试，最终成功

**超时控制验证：**
```javascript
// 应在JavaScript中使用超时
fetchWithTimeout(url, options, 60000)  // 60秒超时
```

---

## 性能验证

### Lighthouse移动评分
```bash
# 使用PageSpeed Insights
# 目标：性能 > 80, 无障碍 > 90
```

**关键指标：**
- ![](https://img.shields.io/badge/FCP-%3C1.5s-green) 首次内容绘制
- ![](https://img.shields.io/badge/LCP-%3C2.5s-green) 最大内容绘制
- ![](https://img.shields.io/badge/CLS-%3C0.1-green) 累积布局偏移

### 网络节流测试
```
场景1: 4G (30 Mbps / 5 Mbps)
场景2: 3G (4 Mbps / 1 Mbps)
场景3: 弱网 (0.5 Mbps / 0.1 Mbps)
```

**预期：** 所有场景下，应用可用（可能缓慢但不崩溃）

---

## 设备测试矩阵

| 设备 | iOS | 屏幕尺寸 | 优先级 | 状态 |
|-----|-----|---------|-------|------|
| iPhone 13/14/15 | 18+ | 390×844 | 🔴 高 | ✅ 需测试 |
| iPhone 12 | 15+ | 390×844 | 🔴 高 | ✅ 需测试 |
| iPhone 11 | 13+ | 326×812 | 🔴 高 | ✅ 需测试 |
| iPhone X | 11+ | 375×812 | 🔴 高 | ✅ 需测试 |
| iPhone 8/7 | 11-17 | 375×667 | 🟡 中 | ✅ 需测试 |
| iPhone SE 2 | 13+ | 375×667 | 🟡 中 | ✅ 需测试 |
| iPad Air | 18+ | 1024×1366 | 🟢 低 | ⏳ 可选 |

| 设备 | Android | 屏幕尺寸 | 优先级 | 状态 |
|-----|---------|---------|-------|------|
| Samsung Galaxy S23 | 14+ | 360×800 | 🔴 高 | ✅ 需测试 |
| Samsung Galaxy A14 | 12+ | 360×800 | 🔴 高 | ✅ 需测试 |
| Xiaomi 13 | 13+ | 360×800 | 🟡 中 | ✅ 需测试 |
| Oppo A76 | 11+ | 360×799 | 🟡 中 | ✅ 需测试 |

---

## 浏览器检查清单

### iOS (Safari/Chrome)
- [ ] 页面加载完整
- [ ] 滑块（宫口开大）可拖动
- [ ] 触摸反馈正常
- [ ] 流式文本显示
- [ ] 模态框动画流畅
- [ ] 返回按钮有效

### Android (Chrome/Firefox)
- [ ] 页面加载完整
- [ ] 输入框获焦无问题
- [ ] 下拉菜单正常
- [ ] 流式响应稳定
- [ ] 后退手势生效
- [ ] 横竖屏切换无误

---

## 故障排除

### 问题1: "分析按钮被遮挡"
```
原因: 安全区未应用
解决: 检查CSS是否包含 env(safe-area-inset-bottom)
```

### 问题2: "流式响应卡住"
```
原因: 浏览器不支持getReader
解决: 检查JavaScript中是否有降级方案
```

### 问题3: "页面闪烁/跳动"
```
原因: 使用了 100vh
解决: 检查CSS是否使用 100dvh
```

### 问题4: "API配置丢失"
```
原因: localStorage不可用（无痕模式）
解决: 检查Console是否有警告，功能是否继续工作
```

### 问题5: "输入框被键盘遮挡"
```
原因: 页面整体缩放
解决: 检查meta viewport是否有 maximum-scale
```

---

## 云端部署检查

### Nginx/Render配置
```bash
# 检查服务器日志查看SSE响应
tail -f /var/log/nginx/access.log | grep analyze/stream

# 预期输出:
# POST /api/analyze/stream 200 ... rt=45.123s
```

### 响应头验证
```bash
curl -i https://your-domain/api/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{...}'

# 应包含:
# Transfer-Encoding: chunked
# Content-Type: text/event-stream
# Access-Control-Allow-Origin: *
```

---

## 最终验证清单

- [ ] ✅ 所有10个功能都已测试
- [ ] ✅ 至少3种设备上测试成功
- [ ] ✅ 网络切换过程无崩溃
- [ ] ✅ 开发者工具无404错误
- [ ] ✅ Console无JavaScript错误
- [ ] ✅ Lighthouse移动评分≥80
- [ ] ✅ 用户反馈无新Bug报告

---

## 反馈报告模板

如发现问题，请提供：
```
【Bug描述】
xxx场景下，xxx功能无法使用

【设备信息】
设备型号: iPhone 13 Pro Max
系统版本: iOS 17.1
浏览器: Safari 17
网络类型: 4G

【复现步骤】
1. ...
2. ...
3. ...

【预期结果】
xxx

【实际结果】
xxx

【错误信息】(Console截图)
```

---

*最后更新: 2026年4月7日*
*维护者: AI Assistant*
