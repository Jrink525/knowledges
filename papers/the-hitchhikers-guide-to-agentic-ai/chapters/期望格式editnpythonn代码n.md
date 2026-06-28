        # 期望格式: edit\n```python\n<代码>\n```
        try:
            new_code = action.split("```python")[1].split("```")[0]
            (self._workdir / "solution.py").write_text(new_code)
            return "文件已成功更新。"
        except IndexError:
            return "编辑失败：请将新代码包裹在 ```python ... ``` 中"

    def _run_tests(self) -> str:
        result = subprocess.run(
            ["python", "-m", "pytest", "test_solution.py",
             "-v", "--tb=short", "--no-header"],
            cwd=self._workdir,
            capture_output=True, text=True,
            timeout=self.TIMEOUT
        )
        return result.stdout + result.stderr

    def _build_observation(self, action_taken: str,
                           test_output: str) -> str:
        code = (self._workdir / "solution.py").read_text()
        return textwrap.dedent(f"""
            任务: {self.task_description}
            步数: {self._step_count}/{self.MAX_STEPS}

            --- 上一步动作 ---
            {action_taken}

            --- 当前 solution.py ---
            {code}

            --- 测试输出 ---
            {test_output}

            --- 可用动作 ---
            view                          # 显示当前文件
            edit\n```python\n<代码>\n```  # 替换文件内容
            run_tests                     # 运行 pytest
            submit                        # 完成并结束回合
        """).strip()


