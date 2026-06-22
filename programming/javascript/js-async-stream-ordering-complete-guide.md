# 深入理解 JavaScript 异步、迭代器与流式保序机制

在对接大语言模型（LLM）流式 API 或处理后端数据流（Stream）时，开发者经常会遇到**文本乱序、打印抖动**等诡异现象。本文基于一次实际的代码排查，深入剖析 `for await...of`、`async/await` 与生成器（Generator）底层的执行机制，并总结出 4 条核心铁律。

---

## 一、问题背景与案例分析

### 1. 现象：明明用了 for await，为什么还是乱序？

假设我们定义了一个标准的流式事件回调接口 ProviderSink：

```typescript
export interface ProviderSink {
  onTextDelta(text: string): void | Promise<void>;
  // ... 其他生命周期回调
}
```

在消费文本流的 async 块中，我们编写了如下代码：

```typescript
// 包含在 async 块内部的消费逻辑
for await (const ev of textStream) {
  // 🚨 隐患发生地：虽然 for await 保证了 ev 是按顺序拿到的
  // 但是我们没有 await 这个异步函数，导致它在后台并发了
  sink.onTextDelta(ev.delta.text);
}
```

**直觉误区**：很多开发者认为 `for await...of` 既然带有 `await`，就会天然地把整个循环体"阻塞同步"执行，数据块 ev 既然是按顺序出来的，那 `sink.onTextDelta` 的执行也应该是严格保序的。

**实际结果**：输出文本彻底乱序（例如本该输出 "你好JavaScript"，实际落地却变成了 "JavaScript好你"）。

### 2. 原因剖析：事件循环（Event Loop）与后台并发

造成异常乱序的真正核心，在于**没有挂起业务回调的 Promise**。我们可以将 `sink.onTextDelta` 的内部耗时抽象化，还原当时的真实时序：

- **第 0ms**：`for await` 拿到第一个字 "你"。同步触发 `sink.onTextDelta("你")`。内部遇到其自身的异步操作（如写库或定时器，耗时 500ms），**由于外层循环没有 await，该函数立刻切断并返回**。外层循环认为这一轮任务已结束，立刻放行。
- **第 100ms**：流吐出第二个字 "好"。同步触发 `sink.onTextDelta("好")`，内部异步耗时 300ms，同样立刻返回。
- **第 200ms**：流吐出第三个字 "J"。同步触发 `sink.onTextDelta("J")`，内部异步耗时 0ms。

此时，JavaScript 引擎的后台队列中同时挂起了数个"赛跑"的异步任务：

```
时间轴 (ms)
─────────────────────────────────────────────────────────────────────>

流的推送:  [Delta 1]("你") ──(100ms)──> [Delta 2]("好") ──(100ms)──> [Delta 3]("J")
              │                         │                         │
循环触发:  onTextDelta("你")         onTextDelta("好")         onTextDelta("J")
              │                         │                         │
异步内部:  (耗时 500ms)              (耗时 300ms)              (耗时 0ms)
              │                         │                         │
              │                         │                         └─> 瞬间完成! (200ms 处)
              │                         └─> 完成! (100ms+300ms = 400ms 处)
              └────────────────────────────────────────────────────> 完成! (0ms+500ms = 500ms 处)
```

最终呈现顺序：**J → 好 → 你**（顺序完全崩塌）

**结论**：`for await...of` 的阻塞只作用于**获取流的下一个数据**，它管不到循环体内部没有被 await 的异步脱缰任务。

### 3. 实际 LLM SDK 中的典型反例

下面是一个高度简化的真实案例，模拟了在封装 LLM 流式 API 时常见的错误写法：

```typescript
// 🚨 反例：真实项目中常见的错误封装
class LLMService {
  async *streamChat(messages: Message[]) {
    const response = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ messages, stream: true }),
    });
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      // 解析 SSE 事件行，yield 出每个 token
      for (const line of text.split("\n")) {
        if (line.startsWith("data: ")) {
          const data = JSON.parse(line.slice(6));
          if (data.choices?.[0]?.delta?.content) {
            yield data.choices[0].delta.content;
          }
        }
      }
    }
  }
}

// 调用方
const llm = new LLMService();

// 🚨 问题：下面三个异步回调全部没 await，后台并发写 UI
for await (const token of llm.streamChat(messages)) {
  appendToUI(token);     // 🚨 未 await
  logToDatabase(token);  // 🚨 未 await
  postToWebSocket(token);// 🚨 未 await
}
```

这种做法在低延迟本地环境可能跑得好好的，一旦 appendToUI/logToDatabase/postToWebSocket 中出现任何异步延迟（数据库写入队列、WebSocket 缓冲区满、UI 渲染帧节流），乱序立刻爆发。

---

## 二、实战演练：Demo 现场抓包

为了彻底看清底层的惰性求值与并发赛跑，我们可以运行以下完整的 TypeScript/JavaScript 实验代码。

### 1. 模拟数据水龙头（异步生成器）

利用 `async function*` 声明一个异步生成器，用来逼真地模拟 LLM 隔 100ms 吐出一个 Token 时的网络延迟：

```typescript
async function* createTextStream() {
  console.log("👉 1. [生成器内部] 激活！开始初始化 chunks...");
  const chunks = ["你", "好", "J", "a", "v", "a", "S", "c", "r", "i", "p", "t"];

  for (const chunk of chunks) {
    // 模拟网络流 100ms 的延迟
    await new Promise((resolve) => setTimeout(resolve, 100));
    yield { delta: { text: chunk } };
  }
}
```

### 2. 错误示范（无 await 导致并发乱序）

```typescript
const badSink = {
  async onTextDelta(text: string) {
    // 故意让先到的字耗时更长，后到的字不耗时
    let delay = 0;
    if (text === "你") delay = 500;
    else if (text === "好") delay = 300;

    await new Promise((resolve) => setTimeout(resolve, delay));
    process.stdout.write(text);
  }
};

async function runBadDemo() {
  console.log("🚀 A. 准备调用 createTextStream()");
  const textStream = createTextStream();
  console.log("🚀 B. textStream 变量赋值完毕（此时函数内部代码甚至还没读到）");

  console.log("-----------------------------------------");
  console.log("🏃 C. 准备进入无 await 的 for await 循环...");

  for await (const ev of textStream) {
    badSink.onTextDelta(ev.delta.text); // 🚨 没加 await
  }
}
```

**控制台预期输出**：

```
🚀 A. 准备调用 createTextStream()
🚀 B. textStream 变量赋值完毕（此时函数内部代码甚至还没读到）
-----------------------------------------
🏃 C. 准备进入无 await 的 for await 循环...
👉 1. [生成器内部] 激活！开始初始化 chunks...
JavaScript好你
```

### 3. 正确示范（严格排队保序）

修复手段极其简单，在循环体调用时加上 await，强行拉住每一次的消费逻辑：

```typescript
async function runGoodDemo() {
  const textStream = createTextStream();
  console.log("\n-----------------------------------------");
  console.log("🏃 D. 准备进入带 await 的保序循环...");

  for await (const ev of textStream) {
    // ✅ 核心修复：必须等待前一次回调彻底决议，才会进入下一次循环去消费流
    await badSink.onTextDelta(ev.delta.text);
  }
}
```

**控制台预期输出**：

```
-----------------------------------------
🏃 D. 准备进入带 await 的保序循环...
👉 1. [生成器内部] 激活！开始初始化 chunks...
你好JavaScript
```

---

## 三、核心归纳：异步与迭代器的 4 条铁律

为了在今后编写复杂异步逻辑时永远不脱轨，请牢记以下四条底层铁律。

### 铁律一：async 函数的"隐式包装"与"紧急刹车"

**口诀：看到 async 返回变 Promise；遇到 await 立即交出控制权。**

- 任何被 `async` 标记的函数，在调用的刹那都会**自动将返回值包装成一个 Promise**。
- 函数内部的代码在遇到第一个 `await` 之前，完全是**同步执行**的。
- **一旦撞上 await，该函数会在原地瞬间按下"冷冻键"**，并立刻切断执行流，向外层的调用者返回一个 pending 状态的 Promise。await 后面的残余代码则被打包成微任务，丢进事件循环队列排队等待被重新唤醒。

**深入理解**：从 ECMAScript 规范角度看，`await` 本质是 `PromiseResolve` + `EnqueuePromiseReactionJob`。`await expr` 等价于：

```typescript
// 编译器的语义等价（简化版）
Promise.resolve(expr).then(
  (value) => { /* 恢复执行 */ },
  (reason) => { /* throw reason */ }
);
```

这也是为什么 `await` 之后的代码**永远在微任务队列中执行**，不会阻塞当前帧的同步代码。

### 铁律二：生成器（\* / yield）的"完全惰性"

**口诀：调用函数不干活，只给一个控制杆；外层不推（.next()），内层不动。**

- 执行 `const textStream = createTextStream()` 时，生成器内部**连第一行代码都还没有读到**（变量尚未初始化）。它仅仅是向内存申请并返回了一个携带 `.next()` 方法的迭代器对象。
- 函数内部的 `yield` 是一个高度听话的"暂停哨卡"。外层循环催动一次（触发底层 `.next()`），内部代码才像蜗牛一样向前挪动一步，直到吐出下一个数据，再度原地陷入冬眠。

**异步生成器 vs 同步生成器**：在 `async function*` 中，`.next()` 本身返回的是一个 `Promise<IteratorResult>`。这意味着每次调用 `.next()` 都会：

1. 创建 Promise
2. 推进生成器内部执行（直到遇到 `yield` 或 `await`）
3. 如果内部有 `await`，先等待它完成
4. 最终 resolve 该 Promise，产出 `{ value, done }`

这种"await + yield 的嵌套调度"是理解 `for await...of` 时序的关键。

### 铁律三：for await...of 的"单向双重阻塞"

**口诀：它是数据流的刹车片，但不是你业务逻辑的紧箍咒。**

`for await` 在底层兼顾两层阻塞：

1. **等数据**：上游的流如果没有产生新包，循环就会卡在门口原地等待。
2. **等循环体清空**：只有当前循环体内的**同步代码跑完**，或者你**显式 await 的 Promise 彻底决议**，循环才会放行，切入下一次迭代去拿流的新数据。

**致命盲区**：如果循环体内启动了一个异步逻辑却没写 await，对 `for await` 而言，它认为同步代码已经清空，便会立刻放行。

**规范层面的还原**（伪代码等价）：

```typescript
// for await (const ev of textStream) { body } 的语义近似于：
const iterator = textStream[Symbol.asyncIterator]();
let result;
while (!(result = await iterator.next()).done) {
  const ev = result.value;
  // ⚠️ 关键：只有这里的 await 能拦住循环
  // 如果 body 里有异步操作但没 await，拦不住
  await body;  // body 就是你的循环体
}
```

### 铁律四：不加 await 的异步调用就是"脱缰的野马"

**口诀：不加 await 的异步调用，等于把任务"发射"到后台，生死顺序听天由命。**

- 在 JavaScript 中，不加 `await` 地调用一个异步函数，本质上只是**同步地"启动"了它**。
- 只要其内部遭遇它自己的 await，控制权返回，外层循环就会继续疯狂运转。此时，后台由于堆积了大量并发的异步任务，谁的网络响应快、谁的延迟短，谁就会在事件循环（Event Loop）中先落地跳出来，从而导致原本在流里严格排队的数据流，最终落地时彻底被打乱。

---

## 四、事件循环视角：await 在微任务队列中的精确位置

要深刻理解乱序的根源，需要理解事件循环的队列优先级。这是大多数教程忽略的关键细节。

### 事件循环执行顺序

```
┌──────────────────────────────┐
│         宏任务 (Macrotask)      │   ← setTimeout, setInterval, I/O callback
│    ┌────────────────────┐     │
│    │   微任务 (Microtask)  │    │   ← Promise.then, async/await 续体
│    │  (全部清空后才放行)   │    │
│    └────────────────────┘     │
│         渲染帧 (requestAnimationFrame)  │  ← 可选，浏览器特有
│    ┌────────────────────┐     │
│    │   下一个宏任务...     │    │
│    └────────────────────┘     │
└──────────────────────────────┘
```

**关键规则**：每个宏任务结束后，事件循环会**完全清空整个微任务队列**，然后才去拉下一个宏任务。微任务队列**不接受优先级插入**，先入队的先执行。

### 当 for await...of 遇上微任务队列

让我们追踪一下正确加 await 的版本中，事件循环是如何严格保证顺序的：

```typescript
for await (const ev of textStream) {
  await sink.onTextDelta(ev.delta.text); // ✅
}
```

**时序展开**（每轮迭代产生一批微任务，严格按入队顺序执行）：

```
Iteration 1:
  sync: iterator.next() → 生成器推进 → yield "你" → Promise resolved
  microtask: for-await 拿到 "你"
  sync: 调用 sink.onTextDelta("你")
  microtask: await 等待它 resolve
  sync: 生成器内部 100ms 定时器 → 宏任务
  [500ms later] sink.onTextDelta 完成 → 微任务触发续体
  microtask: for-await 的下一轮循环体开始

Iteration 2:
  microtask: iterator.next() → 生成器推进
  ...
```

**关键洞察**：加了 `await` 之后，**每一轮迭代的续体（continuation）都排队在上一个 await 决议之后**，相当于在微任务队列中形成了一条**串行链**。而没有 `await` 时，多次 `sink.onTextDelta()` 调用产生的微任务序列是**并列发散**的，它们的 resolve 顺序由内部异步操作的延迟决定。

### 为什么 Promise.all 无序但 map+await 有序

这是理解"并发 vs 保序"的经典对比：

```typescript
// ❌ 并发无序：所有 Promise 同时启动，谁先完成谁先出
const results = await Promise.all(items.map(fetchData));

// ✅ 严格保序：前一个 resolve 后才启动下一个
const results = [];
for (const item of items) {
  results.push(await fetchData(item));
}

// 中间态：并发窗口但保序（下面第五节有详细模式）
```

`for await...of` 中的 await 等价于第二种写法——**天然的串行执行**。

---

## 五、进阶实战：真实场景纠错与优化模式

### 1. LLM 流式渲染的正确姿势

```typescript
// ✅ 正确：逐 token 保序渲染
async function streamAndRender(messages: Message[], uiWriter: UISink) {
  const stream = await openai.chat.completions.create({
    model: "gpt-4",
    messages,
    stream: true,
  });

  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta?.content;
    if (delta) {
      await uiWriter.append(delta); // ✅ 必须 await
    }
  }
}
```

### 2. 缓冲批处理：保序的同时减少 I/O 频率

串行 await 保序但性能较低（每 token 等一次数据库写入）。如果业务允许接收一定的延迟，可以用**缓冲批处理**来平衡：

```typescript
// ✅ 保序缓冲模式：积累一批后批量写入，且保证批次内顺序
async function streamWithBatchWrite(
  stream: AsyncIterable<string>,
  batchSize: number = 10
) {
  let buffer: string[] = [];

  for await (const token of stream) {
    buffer.push(token);

    if (buffer.length >= batchSize) {
      // ✅ 注意：这里也有 await！写入完成后才继续消费流
      await db.batchInsert(buffer.map((t, i) => ({ pos: i, text: t })));
      buffer = [];
    }
  }

  // 清空剩余缓冲
  if (buffer.length > 0) {
    await db.batchInsert(buffer.map((t, i) => ({ pos: i, text: t })));
  }
}
```

### 3. 并发窗口 + 有序输出（高阶模式）

某些场景下串行太慢（例如每个 token 需要调用外部 API 做 enrichment），但最终输出必须保序。这时可以采用**有限并发 + 按序号重排**模式：

```typescript
// ✅ 并发窗口保序模式：用序号发配并发，最终按顺序组装
async function streamWithOrderedConcurrency<T>(
  source: AsyncIterable<T>,
  handler: (item: T) => Promise<string>,
  concurrency: number = 3
): Promise<string[]> {
  const results: Map<number, string> = new Map();
  let index = 0;
  let nextToEmit = 0;
  let active = 0;
  const deferred: Promise<void>[] = [];

  const executor = async (item: T, seq: number) => {
    const output = await handler(item);
    results.set(seq, output);
    active--;
  };

  for await (const item of source) {
    const seq = index++;
    active++;
    deferred.push(executor(item, seq));

    if (active >= concurrency) {
      // 等至少一个任务完成再继续消费流
      await Promise.race(deferred.map((p) => p.then(() => {})));
      // 清理已完成的 deferred（简化示例，实际用 Promise.allSettled 更健壮）
    }
  }

  // 等待所有任务完成
  await Promise.all(deferred);

  // 按序号输出
  return Array.from({ length: index }, (_, i) => results.get(i)!);
}
```

> **注意**：这种模式适合后端批量处理，不适合前端 UI 渲染——因为用户需要等全部完成后才能看到结果。前端场景建议直接用串行 await + 实时渲染。

### 4. 错误处理：生成器抛异常怎么办？

`for await...of` 中的异常处理需要特别注意——生成器内部抛出的错误会直接在 `await iterator.next()` 处抛出：

```typescript
// ✅ 正确的错误处理
async function safeStreamConsume() {
  try {
    for await (const token of streamChat(messages)) {
      try {
        await appendToUI(token);
      } catch (err) {
        // 业务层的异常：记录日志，决定是否继续
        console.error("UI append failed:", err);
        // 根据场景选择 continue 或 break
      }
    }
  } catch (err) {
    // 流本身（生成器）抛出的异常：网络断开、SSE 解析失败等
    console.error("Stream error, reconnecting...", err);
    // 可以在这里实现自动重连逻辑
  }
}
```

### 5. 取消流式处理（AbortController）

长时间运行的数据流需要提供取消机制，否则无法响应用户的"停止生成"操作：

```typescript
async function* cancellableStream(
  url: string,
  signal: AbortSignal
): AsyncGenerator<string> {
  const response = await fetch(url, { signal });
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      // 🚨 关键：这里必须检查 signal，否则即使 AbortController 调用了 abort，
      // 正在 blocking 的 reader.read() 不会自动中断
      if (signal.aborted) {
        await reader.cancel();
        return;
      }

      const { done, value } = await reader.read();
      if (done) break;

      // 解析 SSE 行...
      const text = decoder.decode(value, { stream: true });
      for (const token of parseSSELines(text)) {
        yield token;
      }
    }
  } finally {
    // ✅ 确保无论什么原因退出，都释放资源
    reader.releaseLock();
  }
}

// 使用方式
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000); // 5秒超时

for await (const token of cancellableStream("...", controller.signal)) {
  await appendToUI(token);
}
```

### 6. Convert 模式：将任何流式数据包装为 AsyncIterable

Node.js Readable Stream、EventSource、WebSocket 都可以包装为 `AsyncIterable`，统一用 `for await...of` 消费：

```typescript
// ✅ 将 Node.js Readable Stream 转为 AsyncIterable
async function* readableToAsyncIterable(
  readable: NodeJS.ReadableStream
): AsyncGenerator<Buffer> {
  for await (const chunk of readable) {
    yield chunk;
  }
}

// ✅ 将 EventSource 转为 AsyncIterable
function eventSourceToAsyncIterable(
  url: string,
  eventName: string = "message"
): AsyncIterable<string> {
  return {
    [Symbol.asyncIterator]() {
      const eventSource = new EventSource(url);
      const buffer: string[] = [];
      let resolve: ((value: IteratorResult<string>) => void) | null = null;
      let done = false;

      eventSource.addEventListener(eventName, (event) => {
        if (resolve) {
          resolve({ value: event.data, done: false });
          resolve = null;
        } else {
          buffer.push(event.data);
        }
      });

      eventSource.onerror = () => {
        done = true;
        eventSource.close();
        if (resolve) resolve({ value: undefined, done: true });
      };

      return {
        next() {
          if (buffer.length > 0) {
            return Promise.resolve({ value: buffer.shift()!, done: false });
          }
          if (done) {
            return Promise.resolve({ value: undefined, done: true });
          }
          return new Promise((r) => (resolve = r));
        },
        return() {
          done = true;
          eventSource.close();
          return Promise.resolve({ value: undefined, done: true });
        },
      };
    },
  };
}
```

---

## 六、底层原理深入：AsyncIterator 协议规范

### 1. Symbol.asyncIterator 协议

与同步迭代器的 `Symbol.iterator` 不同，异步迭代器遵循 `Symbol.asyncIterator` 协议：

```typescript
interface AsyncIterator<T> {
  next(value?: any): Promise<IteratorResult<T>>;
  return?(value?: any): Promise<IteratorResult<T>>;
  throw?(exception?: any): Promise<IteratorResult<T>>;
}

interface AsyncIterable<T> {
  [Symbol.asyncIterator](): AsyncIterator<T>;
}
```

**三类核心方法**：

| 方法 | 触发时机 | 默认行为 |
|------|----------|----------|
| `.next()` | 每次循环迭代 | 生成器推进到下一个 `yield` |
| `.return()` | 提前 `break` / `return` / 异常 | 运行 `finally` 块后退出 |
| `.throw()` | 调用方主动注入异常 | 在生成器内部挂起位置抛出 |

### 2. for await...of 的 ECMAScript 规范等价

```typescript
// ES2018 规范定义的 Runtime Semantics: ForIn/OfBodyEvaluation
// 对于 async-iteration 分支，大致等价于：

async function forAwaitOf(iterable, body) {
  const iterator = iterable[Symbol.asyncIterator]();
  const promiseCapability = createPromiseCapability();

  async function iterate() {
    try {
      while (true) {
        // 1. 等 iterator.next() 的 Promise resolve
        const nextResult = await iterator.next();

        // 2. 如果 done，退出
        if (nextResult.done) {
          await iterator.return?.();
          return promiseCapability.resolve(undefined);
        }

        // 3. 执行业务逻辑并等待
        const result = body(nextResult.value);

        // 🚨 第 4 部分的 await body 由 for-await 语法内置
        // 但循环体内部的异步是否需要等待，取决于你写没写 await
        if (result instanceof Promise) {
          await result; // ← 这里如果你没写 await 就不会执行！
        }
      }
    } catch (e) {
      // 如果迭代器有关闭钩子，尝试调用
      if (typeof iterator.throw === "function") {
        await iterator.throw(e);
      }
      throw e;
    }
  }

  iterate();
  return promiseCapability.promise;
}
```

关键的规范细节：**`for await...of` 规范要求每次迭代结束后都会 `await` 一次**，但它 await 的是**循环体表达式的值**。如果你的循环体表达式返回的是一个未 await 的 Promise，这个 Promise 就会直接被 await——但 Promise 代表的异步操作已经"发射"到后台了，await 时它可能已经开始执行了。关键在于它**是否等待了前一个操作的完成**。

### 3. 异步生成器的"暂停-恢复"生命周期

```
调用 createTextStream()
  │
  └─> 创建 AsyncGenerator 对象（内部代码尚未执行）
      │
      └─> 第一次 .next()
          │
          └─> 执行到第一个 await 之前的同步代码
              │
              ├─> await 一个 Promise → 暂停（返回 pending Promise）
              │   │
              │   └─> Promise resolve → 恢复执行 → yield value → 暂停
              │
              └─> 第二次 .next()
                  │
                  └─> 从 yield 之后恢复 → 循环 → 下一个 await → ...
                      │
                      └─> 最后一次 yield → .next() 返回 { done: true }
```

异步生成器内部可以在 `yield` 之间穿插任意多个 `await`，这种灵活组合正是 LLM 流式处理的核心基础。

---

## 七、终极防错决策树

在编写任何流式、异步循环的处理逻辑时，可以通过该决策树进行心理自查：

```
流式数据包到达 (ev)
      │
      ▼
进入 for await 循环体 ──> 执行业务逻辑 sink.onTextDelta(ev)
                              │
                              ├─► 属于纯同步函数？ ────► 【放心，天然保序】
                              │
                              └─► 属于 Async / 返回 Promise？
                                        │
                                        ├─► 加上 await ──► 【强行排队，严格保序（慢，但安全）】
                                        │
                                        │   是否允许缓冲延迟？
                                        │        │
                                        │        ├─► 否 → 保持逐条 await（最安全）
                                        │        │
                                        │        └─► 是 → 用缓冲批处理模式
                                        │                (见第五章第2节)
                                        │
                                        └─► 不加 await ──► 【后台并发，彻底乱序（快，但危险）】
                                                              │
                                                              └─► 如果确实需要并发 + 保序
                                                                   → 用"并发窗口重排模式"
                                                                     (见第五章第3节)
```

---

## 八、速查表

### 8.1 同步 vs 异步迭代器对比

| 特性 | 同步迭代器 | 异步迭代器 |
|------|-----------|-----------|
| 协议 | `Symbol.iterator` | `Symbol.asyncIterator` |
| next() 返回值 | `{ value, done }` | `Promise<{ value, done }>` |
| 消费语法 | `for...of` | `for await...of` |
| 生成器声明 | `function*` | `async function*` |
| 是否惰性 | 是 | 是 |
| 内部可用 await | ❌ | ✅ |
| 每步可挂起 | yield 处 | yield 和 await 处 |

### 8.2 四种常见漏 await 场景

| 场景 | 代码 | 症状 |
|------|------|------|
| 1. 循环体漏 await | `for await (...) { asyncFn() }` | 输出乱序 |
| 2. 回调中漏 await | `.map(async (x) => ...)` | map 返回全是 Promise |
| 3. 事件监听漏 await | `emitter.on("data", async () => ...)` | 事件无序处理 |
| 4. 定时器漏 catch | `setTimeout(async () => ...)` | 静默吞异常 |

### 8.3 快速记忆口诀

| 铁律 | 口诀 |
|------|------|
| async 函数 | 看到 async 返回变 Promise，遇到 await 立即交控制权 |
| 生成器 | 调用函数不干活，只给一个控制杆；外层不推 .next()，内层纹丝不动 |
| for await...of | 等数据也等循环体，但不拦没 await 的野马 |
| 不加 await | 就是发射到后台，谁先跑完谁先赢 |

### 8.4 从问题到解决方案的快速索引

| 问题 | 解决方案 | 参考章节 |
|------|---------|---------|
| 逐 token 保序渲染 | `await` 循环体中的异步调用 | 二-3, 五-1 |
| 性能太慢，想批量写入 | 缓冲批处理模式 | 五-2 |
| 需要并发 + 保序 | 并发窗口 + 序号重排 | 五-3 |
| 流中间断开了，想重连 | try/catch 包裹外层 for await | 五-4 |
| 用户取消生成 | AbortController + signal 检查 | 五-5 |
| Node.js Readable 流 | 包装为 AsyncIterable | 五-6 |
| EventSource 流 | 包装为 AsyncIterable | 五-6 |
