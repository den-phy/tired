# 第 1 周：Python 工程化

这是三个月学习计划的第一个实践仓库。本周目标不是堆功能，而是掌握一个 Python 项目从编写、测试到提交的基本流程。

## 今日任务

1. 阅读 `notes/day01.md`
2. 创建并激活虚拟环境
3. 以可编辑模式安装项目
4. 运行现有测试
5. 完成 `calculator.py` 中标记为 `TODO` 的两个练习
6. 为练习补充测试

## 环境准备

在当前目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## 项目结构

```text
week01-python-engineering/
├── src/
│   └── llm_tools_demo/
│       ├── __init__.py
│       └── calculator.py
├── tests/
│   └── test_calculator.py
├── notes/
│   └── day01.md
├── .env.example
├── .gitignore
├── job-research.md
└── pyproject.toml
```

## 今日完成标准

- `pytest` 全部通过
- 能解释为什么计算器不能直接执行用户输入
- 能解释包、模块、函数和异常分别是什么
- 自己新增至少 2 个测试用例
- 完成一次有意义的 Git Commit

