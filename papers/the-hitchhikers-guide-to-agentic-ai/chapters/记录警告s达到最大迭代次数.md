        # 记录警告：[%s] 达到最大迭代次数
        return ("I reached the maximum number of steps "
                "without completing the task. "
                "Here is what I found so far: "
                + (msg.content or ""))
