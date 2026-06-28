    # 逐步遍历每个子运行（LLM 调用、工具调用等）
    print(f"  Input:  {str(run.inputs)[:200]}")
    print(f"  输入:  {str(run.inputs)[:200]}")
    print(f"  Output: {str(run.outputs)[:200]}")
    print(f"  输出: {str(run.outputs)[:200]}")
    if run.error:
        print(f"  ERROR: {run.error}")
        print(f"  错误: {run.error}")
