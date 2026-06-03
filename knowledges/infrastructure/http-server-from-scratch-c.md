---
title: "Building an HTTP Server from Scratch in C (Step-by-Step)"
tags:
  - c
  - http
  - networking
  - sockets
  - low-level
date: 2026-05-25
source: "https://x.com/thevixhal/status/2058579024008634376"
authors: "Vixhal (@TheVixhal)"
---

# 从零用 C 语言构建 HTTP 服务器

> **来源：** [@TheVixhal](https://x.com/thevixhal/status/2058579024008634376)  
> **代码仓库：** [github.com/vixhal-baraiya/http-server-c](https://github.com/vixhal-baraiya/http-server-c)  
> **核心理念：** 纯 C，无框架、无外部库，只用原始 socket、手动 HTTP 解析、直接与操作系统网络 API 交互。

---

## 最终成果

这个服务器将实现：

- ✅ 打开 socket 并监听端口
- ✅ 接受传入连接
- ✅ 读取并解析 HTTP 请求
- ✅ 发送正确的 HTTP 响应

---

## 前置知识

- 基础 C 语言（指针、struct、字符串）
- Linux 或 macOS 机器（Windows 的 socket API 略有不同）
- 本教程使用 **POSIX socket API**

---

## Step 1：理解 HTTP 到底是什么

在写代码之前，先看 HTTP 请求和响应在文本层面长什么样。

### 浏览器发起的 HTTP 请求

```
GET / HTTP/1.1
Host: localhost:8080
User-Agent: curl/8.0
Accept: */*
```

### 服务器返回的 HTTP 响应

```
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 13

Hello, World!
```

**就是这么简单。** 就是 TCP 连接上传输的纯文本。你的任务：

1. 监听 TCP 连接
2. 读取那段文本
3. 以相同格式写回响应

---

## Step 2：搭建项目

```bash
mkdir http-server && cd http-server
touch server.c
```

编译命令：

```bash
gcc -Wall -Wextra -o server server.c
```

引入所需的头文件：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>         // read(), write(), close()
#include <sys/socket.h>     // socket(), bind(), listen(), accept()
#include <netinet/in.h>     // struct sockaddr_in
#include <arpa/inet.h>      // inet_ntoa()
```

---

## Step 3：创建 Socket

Socket 本质上是一个文件描述符，代表一个网络连接。

```c
int server_fd = socket(AF_INET, SOCK_STREAM, 0);
if (server_fd < 0) {
    perror("socket failed");
    exit(1);
}
```

`socket()` 的三个参数：

| 参数 | 值 | 含义 |
|------|-----|------|
| `AF_INET` | IPv4 | 使用 IPv4 地址族 |
| `SOCK_STREAM` | TCP | 流式套接字（TCP） |
| `0` | 自动选择 | 让 OS 自动选择协议 |

---

## Step 4：设置 Socket 选项（可选但推荐）

不加这个，快速重启服务器时会报 "Address already in use"：

```c
int opt = 1;
if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
    perror("setsockopt failed");
    exit(1);
}
```

`SO_REUSEADDR` 让你在停止服务器后立即重用端口。没有它，OS 会 hold 住端口几分钟，开发时非常烦人。

---

## Step 5：绑定端口（Bind）

创建 socket 并不会把它绑定到任何地址或端口，需要用 `bind()`：

```c
#define PORT 8080

struct sockaddr_in address;
address.sin_family = AF_INET;
address.sin_addr.s_addr = INADDR_ANY;  // 监听所有网络接口
address.sin_port = htons(PORT);        // 主机字节序 → 网络字节序

if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
    perror("bind failed");
    exit(1);
}
```

**关键概念：字节序**
- `htons()` = "host to network short"
- 不同 CPU 存储多字节数字的方式不同（大端 vs. 小端）
- 网络协议统一使用大端（big-endian）

---

## Step 6：开始监听

```c
if (listen(server_fd, 10) < 0) {
    perror("listen failed");
    exit(1);
}
printf("Server listening on port %d...\n", PORT);
```

`listen()` 的第二个参数是 **backlog**——在服务器忙时最多允许多少个连接排队。10 对于简单的服务器足够了。

---

## Step 7：接受连接

`accept()` 会阻塞（暂停执行），直到有客户端连接：

```c
int addrlen = sizeof(address);

while (1) {
    int client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
    if (client_fd < 0) {
        perror("accept failed");
        continue;
    }
    // 处理请求...
    close(client_fd);
}
```

- `while(1)` 让服务器持续运行
- 每次客户端连接，`accept()` 返回一个新的文件描述符 `client_fd`
- 原来的 `server_fd` 继续监听新连接

---

## Step 8：读取 HTTP 请求

```c
char buffer[1024] = {0};
int bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
if (bytes_read < 0) {
    perror("read failed");
    close(client_fd);
    continue;
}

printf("Received request:\n%s\n", buffer);
```

`read()` 从客户端读取最多 `sizeof(buffer) - 1` 字节到 buffer。减 1 是为了留出 null terminator 的位置。

现在打开浏览器访问 `http://localhost:8080`，你会在终端看到原始的 HTTP 请求——这本身就很酷。

---

## Step 9：解析请求（基础版）

不需要完整的 HTTP 解析器，只需提取方法和路径：

```c
void parse_request(const char *request, char *method, char *path) {
    sscanf(request, "%s %s", method, path);
}
```

在循环中使用：

```c
char method[16] = {0};
char path[256] = {0};
parse_request(buffer, method, path);
printf("Method: %s, Path: %s\n", method, path);
```

`sscanf` 从字符串中读取格式化输入。`%s` 读取空格分隔的 token，所以从 `GET / HTTP/1.1` 中能抓到 `GET` 和 `/`。

---

## Step 10：发送 HTTP 响应

```c
void send_response(int client_fd, const char *status, const char *content_type, const char *body) {
    char response[4096];
    int body_len = strlen(body);
    
    snprintf(response, sizeof(response),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        status, content_type, body_len, body);
    
    write(client_fd, response, strlen(response));
}
```

**⚠️ 容易出错的地方：**
- HTTP 要求行尾是 `\r\n`（回车+换行），不是 `\n`
- 空行 `\r\n\r\n` 分隔 headers 和 body
- 务必仔细检查

---

## Step 11：路由请求

```c
void handle_request(int client_fd, const char *method, const char *path) {
    if (strcmp(method, "GET") != 0) {
        send_response(client_fd, "405 Method Not Allowed", "text/plain", "Method not allowed");
        return;
    }
    
    if (strcmp(path, "/") == 0) {
        send_response(client_fd, "200 OK", "text/plain", "Hello from my C server!");
    } else if (strcmp(path, "/about") == 0) {
        send_response(client_fd, "200 OK", "text/plain",
            "This is a simple HTTP server built from scratch in C.");
    } else {
        send_response(client_fd, "404 Not Found", "text/plain", "404: Page not found");
    }
}
```

`strcmp` 比较两个字符串，返回 0 表示相等。

---

## Step 12：完整代码

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 8080

void parse_request(const char *request, char *method, char *path) {
    sscanf(request, "%s %s", method, path);
}

void send_response(int client_fd, const char *status, const char *content_type, const char *body) {
    char response[4096];
    int body_len = strlen(body);
    
    snprintf(response, sizeof(response),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        status, content_type, body_len, body);
    
    write(client_fd, response, strlen(response));
}

void handle_request(int client_fd, const char *method, const char *path) {
    if (strcmp(method, "GET") != 0) {
        send_response(client_fd, "405 Method Not Allowed", "text/plain", "Method not allowed");
        return;
    }
    
    if (strcmp(path, "/") == 0) {
        send_response(client_fd, "200 OK", "text/plain", "Hello from my C server!");
    } else if (strcmp(path, "/about") == 0) {
        send_response(client_fd, "200 OK", "text/plain",
            "This is a simple HTTP server built from scratch in C.");
    } else {
        send_response(client_fd, "404 Not Found", "text/plain", "404: Page not found");
    }
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};

    // 创建 socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket failed"); exit(1); }

    // 设置 SO_REUSEADDR
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt"); exit(1);
    }

    // 绑定
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed"); exit(1);
    }

    // 监听
    if (listen(server_fd, 10) < 0) { perror("listen"); exit(1); }
    printf("🚀 Server listening on http://localhost:%d\n", PORT);

    // 主循环
    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) { perror("accept"); continue; }

        int bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            char method[16] = {0}, path[256] = {0};
            parse_request(buffer, method, path);
            printf("→ %s %s\n", method, path);
            handle_request(client_fd, method, path);
        }

        close(client_fd);
        memset(buffer, 0, sizeof(buffer));
    }

    close(server_fd);
    return 0;
}
```

---

## Step 13：编译与测试

```bash
gcc -Wall -Wextra -o server server.c
./server
```

输出：
```
🚀 Server listening on http://localhost:8080
```

在浏览器或 curl 中测试：

```bash
# 首页 → 200
curl -v http://localhost:8080/

# 关于页 → 200
curl -v http://localhost:8080/about

# 不存在的页面 → 404
curl -v http://localhost:8080/anything-else
```

`curl -v` 会显示完整的请求和响应头，非常适合调试。

---

## 接下来可以扩展的方向

| 功能 | 思路 |
|------|------|
| **多线程/多进程** | `fork()` 或 `pthread_create` 处理并发连接 |
| **文件服务** | 从磁盘读取静态文件并返回 |
| **Keep-Alive** | 支持 HTTP/1.1 持久连接 |
| **Post 请求** | 解析请求体 |
| **路由参数** | 解析 URL 查询参数 |
| **更好的解析器** | 处理边缘情况、错误恢复 |
| **TLS/SSL** | 用 OpenSSL 包装 socket |

---

> **🎉 祝贺！** 你刚刚用纯 C 从零构建了一个 HTTP 服务器。  
> 完整代码在 [github.com/vixhal-baraiya/http-server-c](https://github.com/vixhal-baraiya/http-server-c)  
> 觉得有用的话去点个 ⭐

---

*整理于 2026-05-25，来源：[@TheVixhal](https://x.com/thevixhal/status/2058579024008634376)*
