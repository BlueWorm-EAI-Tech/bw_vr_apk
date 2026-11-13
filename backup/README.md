# APK 备份目录

## Quantum_左右眼交叉版本_20261112.apk

- **版本性质**：左右眼交叉版本（旧版）
- **备份时间**：2026-11-12
- **来源**：从 PICO 4 Ultra（PA921JMGJ9110098G）设备 `com.BlueWormEAI.Quantum` 直接 pull 出的安装包
- **文件大小**：66,604,311 字节
- **特征**：立体显示为左右眼交叉映射 —— 网络端 `left` 视频流被送入右眼纹理、`right` 流送入左眼纹理（`WebRTCReceiver.cs` 交叉赋值），本地双摄预览同样交叉（`StereoCameraRendering.cs`）
- **用途**：与当前版本做 A/B 对比，验证左右眼映射修正后的观感差异

## 当前根目录 Quantum.apk

- **版本性质**：左右眼对应修正版
- **构建时间**：2026-11-12
- **来源分支**：`bw-teleoperate-unity` 仓库 `main` 分支（HEAD `ca11608` + 左右眼映射修正）
- **包名**：`com.BlueWormEAI.Quantum`
- **显示名**：Quantum
- **文件大小**：66,630,363 字节
- **特征**：`left` 视频流 → `leftTexture` → 左眼；`right` 流 → `rightTexture` → 右眼
