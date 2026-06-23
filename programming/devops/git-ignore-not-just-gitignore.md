---
title: ".gitignore 并非 Git 中忽略文件的唯一方式"
tags:
  - git
  - devops
  - workflow
date: 2026-06-18
source: "https://telegra.ph/yr-S4iztq8dSBMxvfMzDxQ-06-18"
authors: "Nelson Figueroa (Hacker News 摘要翻译)"
---

# .gitignore 并非在 Git 中忽略文件的唯一方式

> **来源：** [.gitignore Isn't the Only Way to Ignore Files in Git](https://nelson.cloud/.gitignore-isnt-the-only-way-to-ignore-files-in-git/)

在 Git 中，除了大家熟知的 `.gitignore` 以外，还有另外两种方式可以用来忽略文件。

---

## 三种忽略机制对比

### 1. `.gitignore` 文件（共享级，最常用）

该文件位于代码仓库中，会随着其他代码一起提交并同步到 Git。添加到该文件中的规则对所有参与项目的开发者共享。

- ✅ 项目中所有人都共用
- ✅ 随仓库版本管理
- ❌ 不适合放个人偏好

### 2. `.git/info/exclude` 文件（仓库级，不提交）

每个 Git 仓库的 `.git` 目录下都有一个 `exclude` 文件。修改它不会被提交。

**适合放个人习惯的忽略规则。** 比如你在某个仓库里写了一篇 `notes.txt`，不想提交也不影响别的开发者，就放这里。

### 3. `~/.config/git/ignore` 全局文件（机器级，全局生效）

对当前电脑上所有 Git 仓库生效，不与特定项目关联。

适合放系统生成的临时文件，例如 macOS 的 `.DS_Store`。

**自定义全局忽略文件路径：**

```bash
git config --global core.excludesFile ~/.gitignore_global
```

**恢复默认：**

```bash
git config --global --unset core.excludesFile
```

---

## 如何检查文件被哪个规则忽略

使用 `git check-ignore -v <文件名>` 命令查询：

| 忽略来源 | 示例输出 |
|----------|---------|
| `.gitignore` | `:1:.DS_Store .DS_Store` |
| `.git/info/exclude` | `.git/info/exclude:7:.DS_Store .DS_Store` |
| 全局配置 | `/Users/nelson/.config/git/ignore:2:.DS_Store .DS_Store` |
| 自定义全局文件 | `/Users/nelson/.gitignore_global:1:.DS_Store .DS_Store` |

如果文件没有被任何规则忽略，命令不会产生任何输出。

---

原文：[https://nelson.cloud/.gitignore-isnt-the-only-way-to-ignore-files-in-git/](https://nelson.cloud/.gitignore-isnt-the-only-way-to-ignore-files-in-git/)
评论：[https://news.ycombinator.com/item?id=48583356](https://news.ycombinator.com/item?id=48583356)

*整理于 2026-06-23*
