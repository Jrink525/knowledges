            # SSE format: "data: <json>\n\n"
            yield f"data: {json.dumps({'token': delta.content})}\n\n"
        elif chunk.choices[0].finish_reason:
            yield f"data: {json.dumps({'done': True})}\n\n"


@app.get("/stream")
async def stream_endpoint(prompt: str):
    return StreamingResponse(
        token_stream(prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
\end{lstlisting}

\subsection{Tool Call Streaming}
\label{tool-call-streaming}
\subsection{工具调用流式 (Tool Call Streaming)}
\label{tool-call-streaming}

Modern LLM APIs support streaming tool calls: the tool name and arguments are streamed incrementally, enabling the UI to show ``Agent is calling \texttt{search\_web} with query: ‘climate change 2024’\ldots{}'' before the tool has even been invoked. This requires parsing partial JSON, which can be done with streaming JSON parsers.
现代 LLM API 支持流式工具调用：工具名称和参数逐步流式传输，使得 UI 能够在工具被实际调用前就显示“智能体正在调用 \texttt{search\_web}，查询为：‘climate change 2024’……”。这需要解析部分 JSON，可使用流式 JSON 解析器完成。

Patterns for tool call streaming:
工具调用流式的模式：

\begin{itemize}
  \item \textbf{Progressive argument display}: Show tool arguments as they stream in, even before the call is complete.
  \item \textbf{渐进式参数显示}：在调用完成前，随着参数流式输入逐步显示工具参数。
  \item \textbf{Parallel tool call indicators}: When the model calls multiple tools simultaneously, show all of them as pending, then update each as results arrive.
  \item \textbf{并行工具调用指示器}：当模型同时调用多个工具时，将它们全部显示为待处理状态，然后随着结果到达分别更新。
  \item \textbf{Tool result streaming}: Some tools (e.g., code execution, web scraping) can themselves stream results; pipe these through to the UI progressively.
  \item \textbf{工具结果流式传输}：某些工具（如代码执行、网页抓取）自身可以流式传输结果；将这些结果逐步传递到 UI。
\end{itemize}

\subsection{Multi-Agent Streaming}
\label{multi-agent-streaming}
\subsection{多智能体流式 (Multi-Agent Streaming)}
\label{multi-agent-streaming}

In multi-agent systems, multiple agents may be generating output simultaneously. The UI must handle parallel streams:
在多智能体系统中，多个智能体可能同时生成输出。UI 必须处理并行流：

\begin{itemize}
  \item \textbf{Agent-labeled streams}: Each stream is tagged with the agent’s identity; the UI renders them in separate lanes or panels.
  \item \textbf{智能体标记流}：每个流带有智能体身份标签；UI 将其渲染在单独的通道或面板中。
  \item \textbf{Stream merging}: For supervisor-subagent patterns, the supervisor’s stream may interleave with subagent streams; the UI must maintain coherent ordering.
  \item \textbf{流合并}：对于监督者-子智能体模式，监督者的流可能与子智能体的流交错；UI 必须保持一致的顺序。
  \item \textbf{Backpressure}: If the UI cannot render as fast as streams arrive (e.g., multiple agents generating simultaneously), a backpressure mechanism must prevent buffer overflow. Strategies include: dropping intermediate tokens (showing only the latest), batching updates, or pausing slower streams.
  \item \textbf{背压 (Backpressure)}：如果 UI 的渲染速度跟不上流到达的速度（例如多个智能体同时生成），必须采用背压机制防止缓冲区溢出。策略包括：丢弃中间令牌（仅显示最新）、批量更新或暂停较慢的流。
\end{itemize}

\subsection{Optimistic UI Updates}
\label{optimistic-ui-updates}
\subsection{乐观 UI 更新 (Optimistic UI Updates)}
\label{optimistic-ui-updates}

Optimistic UI updates improve perceived responsiveness by immediately reflecting user actions in the UI before server confirmation:
乐观 UI 更新通过在服务器确认之前立即在 UI 中反映用户操作，提升感知响应速度：

\begin{itemize}
  \item When a user sends a message, it appears immediately in the chat history (optimistically) while the request is in flight.
  \item 当用户发送消息时，该消息会立即（乐观地）出现在聊天历史中，同时请求正在传输中。
  \item When an approval gate is accepted, the UI immediately shows the action as ``approved'' and begins showing the agent’s next steps, even before the server has processed the approval.
  \item 当批准门控被接受时，UI 立即显示该操作为“已批准”，并开始展示智能体的后续步骤，即使服务器尚未处理该批准。
  \item If the server returns an error, the optimistic update is rolled back and an error state is shown.
  \item 如果服务器返回错误，则回滚乐观更新并显示错误状态。
\end{itemize}

\subsection{Backpressure Handling}
\label{backpressure-handling}
\subsection{背压处理 (Backpressure Handling)}
\label{backpressure-handling}

In high-throughput agentic scenarios, the rate of incoming data can exceed the UI’s rendering capacity. Strategies for managing backpressure:
在高吞吐量的智能体场景中，传入数据速率可能超过 UI 的渲染能力。管理背压的策略如下：

\begin{itemize}
  \item \textbf{Token batching}: Buffer tokens for 50--100ms and render in batches rather than one-by-one, reducing DOM update frequency.
  \item \textbf{令牌批处理}：将令牌缓冲 50--100ms 后分批渲染，而非逐个渲染，从而降低 DOM 更新频率。
  \item \textbf{Virtual scrolling}: For long outputs, render only the visible portion of the content, discarding off-screen DOM nodes.
  \item \textbf{虚拟滚动}：对于长输出，仅渲染内容的可见部分，丢弃屏幕外的 DOM 节点。
  \item \textbf{Throttled updates}: For metrics and status displays, update at a fixed rate (e.g., 10 Hz) regardless of the incoming data rate.
  \item \textbf{节流更新}：对于指标和状态显示，以固定速率（例如 10 Hz）更新，不受传入数据速率影响。
  \item \textbf{Progressive detail}: Show a summary view during high-throughput periods; full detail available on demand.
  \item \textbf{渐进式细节}：在高吞吐量期间显示摘要视图；按需提供完整细节。
\end{itemize}

\section{Human-in-the-Loop UI Design}
\label{subsec:hitl-design}
\section{人在回路中 UI 设计 (Human-in-the-Loop UI Design)}
\label{subsec:hitl-design}

Human-in-the-loop (HITL) interaction is one of the most consequential design challenges in agentic UIs. The goal is to maintain meaningful human oversight without creating a bottleneck that negates the efficiency benefits of automation.
人在回路中（HITL）交互是智能体 UI 中最关键的设计挑战之一。目标是保持有意义的人类监督，同时避免形成抵消自动化效率优势的瓶颈。

\subsection{When to Interrupt the Agent}
\label{when-to-interrupt-the-agent}
\subsection{何时中断智能体 (When to Interrupt the Agent)}
\label{when-to-interrupt-the-agent}

Not all agent actions warrant human review. A principled interruption policy considers:
并非所有智能体行为都需要人工审查。有原则的中断策略需考虑：

\begin{itemize}
  \item \textbf{Reversibility}: Irreversible actions (deleting files, sending emails, making purchases) always warrant approval. Reversible actions (reading files, searching the web) generally do not.
  \item \textbf{可逆性}：不可逆操作（删除文件、发送邮件、购买）始终需要批准。可逆操作（读取文件、搜索网络）通常不需要。
  \item \textbf{Scope}: Actions affecting external systems or other people warrant more scrutiny than purely local actions.
  \item \textbf{范围}：影响外部系统或其他人的操作比纯本地操作需要更严格的审查。
  \item \textbf{Confidence}: When the agent’s confidence in its interpretation of the user’s intent is low, it should ask for clarification rather than proceed.
  \item \textbf{置信度}：当智能体对用户意图解释的置信度较低时，应请求澄清而非继续执行。
  \item \textbf{Cost}: High-cost actions (large API calls, expensive computations) warrant approval.
  \item \textbf{成本}：高成本操作（大量 API 调用、昂贵计算）需要批准。
  \item \textbf{Novelty}: Actions the agent has not taken before in this context warrant more scrutiny than routine actions.
  \item \textbf{新颖性}：智能体在此上下文中未执行过的操作比常规操作需要更多审查。
\end{itemize}

\subsection{Tiered Approval Workflows}
\label{tiered-approval-workflows}
\subsection{分层审批工作流 (Tiered Approval Workflows)}
\label{tiered-approval-workflows}

A tiered approval policy balances oversight with efficiency:
分层审批策略在监督与效率之间取得平衡：

\begin{keybox}[Three-Tier Approval Model]
\textbf{Tier 1 (Auto-approve):} Low-risk, reversible, routine actions. Examples: web search, reading files, calling read-only APIs. The agent proceeds without interruption; actions are logged for audit.

\textbf{第1层（自动批准）：}低风险、可逆、常规操作。例如：网络搜索、读取文件、调用只读 API。智能体无需中断继续执行；操作记录在日志中供审计。

\textbf{Tier 2 (Notify):} Medium-risk actions. The UI shows a non-blocking notification (``Agent sent a draft email to your Drafts folder'') that the user can review asynchronously. A brief window (e.g., 30 seconds) allows cancellation before the action is finalized.

\textbf{第2层（通知）：}中等风险操作。UI 显示非阻塞通知（“智能体将草稿邮件发送到您的草稿箱”），用户可异步审查。在操作最终确定前有短暂窗口（例如 30 秒）允许取消。

\textbf{Tier 3 (Require approval):} High-risk, irreversible, or high-cost actions. The agent pauses and presents a blocking approval gate. The user must explicitly approve, reject, or modify before the agent continues.

\textbf{第3层（需批准）：}高风险、不可逆或高成本操作。智能体暂停并呈现阻塞式批准门控。用户必须明确批准、拒绝或修改后，智能体才能继续。
\end{keybox}

The thresholds between tiers can be configured by the user (``always ask before sending emails'') or learned from user behavior (if the user always approves web searches, auto-approve them in the future).
各层之间的阈值可由用户配置（“发送邮件前始终询问”）或从用户行为中学习（如果用户始终批准网络搜索，则未来自动批准）。

\subsection{Feedback Mechanisms}
\label{feedback-mechanisms}
\subsection{反馈机制 (Feedback Mechanisms)}
\label{feedback-mechanisms}

Beyond approval gates, agentic UIs should provide rich feedback mechanisms that help the agent improve over time:
除了批准门控，智能体 UI 还应提供丰富的反馈机制，帮助智能体随时间改进：

\begin{itemize}
  \item \textbf{Thumbs up/down}: Simple binary feedback on responses, stored and used for RLHF fine-tuning or preference learning.
  \item \textbf{Thumbs up/down（点赞/点踩）}：对响应的简单二元反馈，存储并用于RLHF微调或偏好学习。
  \item \textbf{Inline corrections}: Users can directly edit agent outputs; the delta between the original and corrected output is a training signal.
  \item \textbf{Inline corrections（内联修正）}：用户可以直接编辑智能体的输出；原始输出与修正输出之间的差异即为训练信号。
  \item \textbf{Preference selection}: When the agent offers multiple options, the user’s selection is a preference signal.
  \item \textbf{Preference selection（偏好选择）}：当智能体提供多个选项时，用户的选择即为偏好信号。
  \item \textbf{Explicit instruction}: ``Don’t do this again'', ``Always ask before X'', ``Prefer approach Y over Z''---natural language instructions that update the agent’s behavioral policy.
  \item \textbf{Explicit instruction（显式指令）}：“别再这样做了”、“在X之前始终询问”、“优先采用方法Y而非Z”——这些自然语言指令用于更新智能体的行为策略。
  \item \textbf{Rating with rationale}: Optional free-text explanation accompanying a rating, providing richer signal than binary feedback.
  \item \textbf{Rating with rationale（带理由的评分）}：评分时附带的可选自由文本解释，提供比二元反馈更丰富的信号。
\end{itemize}

\subsection{Teaching the Agent Through UI Interaction}
\subsection{通过UI交互教导智能体}
\label{teaching-the-agent-through-ui-interaction}

The most sophisticated HITL UIs treat every interaction as a teaching opportunity:
最先进的HITL UI将每一次交互都视为教学机会：

\begin{itemize}
  \item \textbf{Demonstration}: The user performs a task manually; the agent observes and learns the preferred approach.
  \item \textbf{Demonstration（示范）}：用户手动执行任务；智能体观察并学习偏好方法。
  \item \textbf{Correction with generalization}: When the user corrects an agent action, the UI asks ``Should I always do this differently?'' to generalize the correction.
  \item \textbf{Correction with generalization（带泛化的修正）}：当用户修正智能体的某个行为时，UI会询问“我是否应当始终以不同方式执行此操作？”以泛化该修正。
  \item \textbf{Preference elicitation}: Periodic prompts asking the user to compare two agent behaviors and indicate which is preferred.
  \item \textbf{Preference elicitation（偏好引示）}：定期提示用户比较两种智能体行为，并指出更偏好哪一种。
  \item \textbf{Behavioral profiles}: The UI maintains a visible ``preferences'' profile that the user can review and edit, making the agent’s learned behaviors transparent and controllable.
  \item \textbf{Behavioral profiles（行为档案）}：UI维护一个可见的“偏好”档案，用户可以查看和编辑，使智能体习得的行为透明可控。
\end{itemize}

\section{Accessibility and Trust}
\section{可访问性与信任}
\label{subsec:ui-trust}

Trust is not a feature---it is an emergent property of a system that consistently behaves as expected, explains itself clearly, and recovers gracefully from failures. Agentic UIs must be designed with trust as a first-class concern.
信任并非一项功能——而是系统持续按预期运作、清晰解释自身行为、并从故障中优雅恢复时涌现出的属性。智能体UI在设计时必须将信任作为首要考量。

\subsection{Explaining Agent Decisions}
\subsection{解释智能体决策}
\label{explaining-agent-decisions}

Explainability in agentic UIs goes beyond showing chain-of-thought. It requires:
智能体UI中的可解释性不仅限于展示思维链。它要求：

\begin{itemize}
  \item \textbf{Decision rationale}: For consequential decisions, the agent should explain not just \emph{what} it decided but \emph{why}---which factors were considered, what alternatives were rejected, and what assumptions were made.
  \item \textbf{Decision rationale（决策理由）}：对于有重大影响的决策，智能体不仅应解释其 \emph{做了什么}决策，还应说明 \emph{为什么}——考虑了哪些因素、拒绝了哪些备选方案、以及做出了哪些假设。
  \item \textbf{Source attribution}: Claims should be linked to their sources; retrieved documents should be citable.
  \item \textbf{Source attribution（来源归因）}：主张应链接至其来源；检索到的文档应可引用。
  \item \textbf{Counterfactual explanations}: ``If you had said X instead of Y, I would have done Z''---helping users understand the agent’s decision boundary.
  \item \textbf{Counterfactual explanations（反事实解释）}：“如果你当时说X而不是Y，我会做Z”——帮助用户理解智能体的决策边界。
  \item \textbf{Uncertainty quantification}: Explicit statements of confidence, with the factors driving uncertainty.
  \item \textbf{Uncertainty quantification（不确定性量化）}：明确给出置信度声明，并说明导致不确定性的因素。
\end{itemize}

\subsection{Showing Confidence Levels}
\subsection{展示置信水平}
\label{showing-confidence-levels}

Confidence indicators must be calibrated and meaningful:
置信度指标必须经过校准且具有实际意义：

\begin{itemize}
  \item \textbf{Verbal confidence}: Natural language expressions (``I’m fairly confident'', ``I’m not sure about this'') are more interpretable than numerical probabilities for most users.
  \item \textbf{Verbal confidence（言语置信度）}：对大多数用户而言，自然语言表达（“我相当确信”、“我不太确定这一点”）比数值概率更易理解。
  \item \textbf{Visual confidence}: Color coding (green/yellow/red), icon variants, or font weight can encode confidence without adding text.
  \item \textbf{Visual confidence（视觉置信度）}：颜色编码（绿/黄/红）、图标变体或字体粗细可在不增加文字的情况下编码置信度。
  \item \textbf{Confidence by claim}: For multi-claim responses, per-claim confidence indicators (e.g., inline footnotes) are more informative than a single response-level score.
  \item \textbf{Confidence by claim（逐条置信度）}：对于包含多条主张的响应，逐条置信度指示（例如内联脚注）比单一的整体响应分数信息量更大。
\end{itemize}

\subsection{Undo and Rollback Capabilities}
\subsection{撤销与回滚能力}
\label{undo-and-rollback-capabilities}

Every consequential agent action should be undoable where technically feasible:
在技术可行的情况下，每一项有重大影响的智能体操作都应可撤销：

\begin{itemize}
  \item \textbf{Action log with undo}: A chronological log of all agent actions with an ``Undo'' button for each reversible action.
  \item \textbf{Action log with undo（带撤销的操作日志）}：按时间顺序记录所有智能体操作，并为每个可逆操作提供“撤销”按钮。
  \item \textbf{Snapshot-based rollback}: For stateful tasks (e.g., code editing, document writing), periodic snapshots enable rollback to any prior state.
  \item \textbf{Snapshot-based rollback（基于快照的回滚）}：对于有状态的任务（如代码编辑、文档撰写），定期快照可回滚到任意先前状态。
  \item \textbf{Dry-run mode}: Before executing a plan, the agent can simulate it and show the predicted state changes, allowing the user to approve or modify before any real action is taken.
  \item \textbf{Dry-run mode（试运行模式）}：在执行计划之前，智能体可以模拟运行并显示预测的状态变化，允许用户在实际执行前批准或修改。
  \item \textbf{Graceful degradation}: When an undo is not possible (e.g., an email has been sent), the UI clearly communicates this and offers the best available alternative (e.g., sending a follow-up).
  \item \textbf{Graceful degradation（优雅降级）}：当无法撤销时（例如邮件已发送），UI明确告知用户，并提供最佳的可行替代方案（例如发送后续邮件）。
\end{itemize}

\subsection{Audit Trails in the UI}
\subsection{UI中的审计追踪}
\label{audit-trails-in-the-ui}

For enterprise and regulated use cases, audit trails are essential:
对于企业和受监管的使用场景，审计追踪至关重要：

\begin{itemize}
  \item \textbf{Immutable action log}: Every agent action, tool call, and human approval is logged with timestamp, user identity, and full parameters.
  \item \textbf{Immutable action log（不可变操作日志）}：每一次智能体操作、工具调用和人工审批均记录时间戳、用户身份和完整参数。
  \item \textbf{Exportable history}: The audit trail can be exported as JSON, CSV, or PDF for compliance reporting.
  \item \textbf{Exportable history（可导出的历史记录）}：审计追踪可导出为JSON、CSV或PDF格式，用于合规报告。
  \item \textbf{Diff views}: For document or code modifications, the audit trail includes before/after diffs.
  \item \textbf{Diff views（差异视图）}：对于文档或代码修改，审计追踪包含修改前后的差异对比。
  \item \textbf{Session replay}: The ability to replay an entire agent session, step by step, for debugging or compliance review.
  \item \textbf{Session replay（会话重放）}：能够逐步重放完整的智能体会话，用于调试或合规审查。
\end{itemize}

\subsection{Managing User Expectations}
\subsection{管理用户期望}
\label{managing-user-expectations}

Miscalibrated expectations are a primary source of user distrust. Agentic UIs should actively manage expectations:
期望失准是用户不信任的主要来源。智能体UI应主动管理期望：

\begin{itemize}
  \item \textbf{Capability disclosure}: Clear, accessible documentation of what the agent can and cannot do.
  \item \textbf{Capability disclosure（能力披露）}：清晰易懂地记录智能体能够做什么和不能做什么。
  \item \textbf{Limitation acknowledgment}: When the agent encounters a task outside its capabilities, it says so clearly rather than attempting and failing silently.
  \item \textbf{Limitation acknowledgment（局限性承认）}：当智能体遇到超出其能力的任务时，应明确告知，而不是尝试后无声失败。
  \item \textbf{Uncertainty communication}: Proactive communication of uncertainty, rather than waiting for the user to discover errors.
  \item \textbf{Uncertainty communication（不确定性沟通）}：主动沟通不确定性，而不是等待用户发现错误。
  \item \textbf{Consistent persona}: A consistent agent identity and communication style builds familiarity and predictability.
  \item \textbf{Consistent persona（一致的角色形象）}：一致的智能体身份和沟通风格可建立熟悉感和可预测性。
\end{itemize}

\begin{examplebox}[Trust-Building Through Transparency: A Case Study]
Consider an agent tasked with booking a flight. A low-trust UI presents: ``I’ve booked your flight. Confirmation: AA1234.'' A high-trust UI presents: (1) a summary of the search parameters used, (2) the alternatives considered and why this flight was selected, (3) the exact actions taken (API calls to the booking system), (4) the confirmation details with a link to the booking, (5) an undo option valid for the next 24 hours, and (6) a note about what the agent cannot do (e.g., ``I cannot modify this booking; you’ll need to call the airline directly''). The second UI takes more screen space but builds the user’s confidence that the agent acted correctly and gives them the information needed to verify and recover if needed.
\begin{examplebox}[通过透明度建立信任：一个案例研究]
设想一个负责预订航班的智能体。低信任度的UI显示：“我已为您预订了航班。确认号：AA1234。”高信任度的UI则展示：(1) 所使用的搜索参数摘要，(2) 考虑过的备选方案以及选择该航班的原因，(3) 执行的具体操作（对预订系统的API调用），(4) 包含预订链接的确认详情，(5) 未来24小时内有效的撤销选项，以及(6) 关于智能体不能做什么的说明（例如“我无法修改此预订；您需要直接联系航空公司”）。第二种UI占用更多屏幕空间，但能让用户确信智能体操作正确，并提供验证和必要时恢复所需的信息。
\end{examplebox}

\section{Implementation Example: A Full-Stack Agentic UI}
\section{实现示例：一个全栈智能体UI}
\label{subsec:ui-implementation}

We now present a concrete implementation example combining streaming, tool visualization, and approval gates in a Python/React stack. The backend uses FastAPI with LangGraph; the frontend uses React with the Vercel AI SDK patterns adapted for a custom backend.
我们现在展示一个具体的实现示例，它结合了流式传输、工具可视化和审批门控，采用Python/React技术栈。后端使用FastAPI与LangGraph；前端使用React，并适配Vercel AI SDK模式以支持自定义后端。

\subsection{Backend: FastAPI + LangGraph with Streaming and Approval Gates}
\subsection{后端：带流式传输和审批门控的FastAPI + LangGraph}
\label{backend-fastapi-langgraph-with-streaming-and-approval-gates}

\begin{lstlisting}[style=pythonstyle, caption={FastAPI backend with streaming and approval gates}]
