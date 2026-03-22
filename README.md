# Kimi Coding Plan

这是 FamilyClaw 的 Kimi Coding Plan AI Provider 插件。

它的作用很直接：把家庭里的 AI Provider 接到 Kimi Coding Plan，让需要代码规划、快速推理和结构化文本回复的场景可以直接走 Kimi 的接口。

## 适合什么场景

- 想在 FamilyClaw 里接入 Kimi Coding Plan 作为 AI Provider
- 希望优先使用 Kimi Coding 专用接口，而不是通用模型入口
- 需要更偏稳定、快速的短文本和快任务响应

## 插件特点

- 默认使用 Kimi Coding 专用 Anthropic 兼容地址
- 保留 Moonshot Anthropic 兼容地址作为兼容选项
- 对快任务自动收紧上下文和输出长度，减少延迟

## 配置时需要准备什么

- 一个可用的 Kimi Coding Plan API Key
- 你希望在 FamilyClaw 里展示的提供方名称

## 基本使用方式

1. 安装并启用插件
2. 填写 `API Key`
3. 选择或确认 `Base URL`

## 已知限制

- 当前主要面向文本能力
- 默认不做模型自动发现
- 插件本身不提供额外的远程执行能力，只负责 Provider 接入

## 兼容性

- 插件版本：`0.2.1`
- 最低宿主版本：`0.1.0`
