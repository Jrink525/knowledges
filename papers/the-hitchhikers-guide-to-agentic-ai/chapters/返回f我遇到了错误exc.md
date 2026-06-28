                # 返回：f"我遇到了错误：{exc}"

            choice  = response.choices[0]
            msg     = choice.message
            finish  = choice.finish_reason

