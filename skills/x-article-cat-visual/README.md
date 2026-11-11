# X 文章布偶猫智能配图 Skill

这是根据本会话 V4.0 规则及历次反馈整理的 Skill 文件夹。

## 包内文件

- `SKILL.md`：执行步骤与工具交付约束（入口）
- `assets/ragdoll-ip-reference.jfif`：用户本会话上传的固定猫咪参考照片
- `references/visual-spec.md`：详细角色风格、构图、文字要求
- `references/session-history.md`：已画过的画面类型和防重复提醒
- `scripts/export_image.py`：用 Pillow 等比例导出并核验目标尺寸

## 使用

将整个 `x-article-cat-visual` 文件夹复制到你使用的 AI Agent 的 Skills 目录（如对应环境支持），然后提供文章标题、正文、类型和特殊要求，并明确要求按照本 Skill 生成图片。Agent 需要有可用的生图能力，及可选的 Python/Pillow 以完成尺寸处理。安装时请根据具体 Agent 当前的 Skill 目录规范操作。

如只想在 ChatGPT/生图对话中粘贴指令，请使用另行交付的 `X文章智能配图_V4.0_完整提示词.md`，并上传本包中的猫咪参考图。

**注意**：Skill 不等于生图模型；无生图工具时无法直接输出图片。最终像素须检查文件真实尺寸。
