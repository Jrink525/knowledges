---
title: "Java Agent 从入门到生产实战：原理、字节码增强与踩坑指南"
tags:
  - java
  - java-agent
  - bytecode
  - instrumentation
  - asm
  - bytebuddy
  - javassist
  - performance
  - apm
  - opentelemetry
date: 2026-05-29
source: "综合整理自微信公众号、Baeldung、InfoQ、Medium、Oracle 官方文档、javathinking.com 等"
---

# Java Agent 从入门到生产实战：原理、字节码增强与踩坑指南

> **一句话总结**：Java Agent 是 JVM 提供的钩子机制，允许在类加载前/运行时修改字节码。它是 APM（SkyWalking、Pinpoint）、热部署（JRebel）、调试工具（Arthas）和可观测性（OpenTelemetry）等技术的基石。本文从原理到生产踩坑，覆盖完整知识体系。

---

## 目录

1. [背景故事：为什么需要 Java Agent？](#1-背景故事为什么需要-java-agent)
2. [JVM Instrumentation 核心原理](#2-jvm-instrumentation-核心原理)
   - [2.1 Instrumentation 接口](#21-instrumentation-接口)
   - [2.2 ClassFileTransformer 机制](#22-classfiletransformer-机制)
   - [2.3 类加载的生命周期拦截](#23-类加载的生命周期拦截)
3. [两种 Agent 模式：Premain vs Agentmain](#3-两种-agent-模式premain-vs-agentmain)
   - [3.1 Premain：启动时静态挂载](#31-premain启动时静态挂载)
   - [3.2 Agentmain：运行时动态 Attach](#32-agentmain运行时动态-attach)
   - [3.3 Attach API 详解](#33-attach-api-详解)
4. [手写第一个 Java Agent（ASM 方式）](#4-手写第一个-java-agentasm-方式)
5. [三大字节码框架选型](#5-三大字节码框架选型)
   - [5.1 ASM：底层性能王者](#51-asm底层性能王者)
   - [5.2 Javassist：字符串模板为王](#52-javassist字符串模板为王)
   - [5.3 Byte Buddy：现代声明式 API](#53-byte-buddy现代声明式-api)
   - [5.4 选型对比表](#54-选型对比表)
6. [实战案例：构建方法耗时监控 Agent](#6-实战案例构建方法耗时监控-agent)
7. [生产级最佳实践](#7-生产级最佳实践)
   - [7.1 性能优化](#71-性能优化)
   - [7.2 安全与稳定性](#72-安全与稳定性)
   - [7.3 兼容性](#73-兼容性)
   - [7.4 包冲突与 Shade 技术](#74-包冲突与-shade-技术)
8. [血泪踩坑实录](#8-血泪踩坑实录)
   - [8.1 ClassLoader 地狱](#81-classloader-地狱)
   - [8.2 核心 JDK 类篡改的灾难](#82-核心-jdk-类篡改的灾难)
   - [8.3 重入变换与栈溢出](#83-重入变换与栈溢出)
   - [8.4 启动耗时爆炸](#84-启动耗时爆炸)
   - [8.5 Metaspace 内存泄漏](#85-metaspace-内存泄漏)
   - [8.6 跨 JVM 版本的字节码兼容性](#86-跨-jvm-版本的字节码兼容性)
9. [工业级案例：OpenTelemetry Java Agent](#9-工业级案例opentelemetry-java-agent)
10. [诊断与调试工具链](#10-诊断与调试工具链)
11. [总结](#11-总结)

---

## 1. 背景故事：为什么需要 Java Agent？

### 一个真实的故事

团队在做性能优化时，有人为了定位慢方法，写了一大堆这样的代码：

```java
@Override
public void method(Req req) {
    StopWatch stopWatch = new StopWatch();
    stopWatch.start("某某方法-耗时统计");
    method();
    stopWatch.stop();
    log.info("查询耗时分布：{}", stopWatch.prettyPrint());
}
```

类似的代码散布在整个项目中，**侵入性极强**。如果要删掉这些监控代码，得翻遍所有文件。这就是典型的手动埋点困局。

### 解决方案

Java Agent 可以**无侵入**地解决这类问题——不需要修改源码，不需要重新编译，甚至可以在生产环境运行时动态挂载：

```java
// 一行命令即可附加监控
java -javaagent:monitor-agent.jar -jar myapp.jar
```

### 技术基石地位

Java Agent 是以下知名技术的共同根基：

| 技术 | 用途 | 用户规模 |
|------|------|---------|
| **SkyWalking** | APM 分布式追踪 | 国内最广的 Java APM |
| **Arthas** | 在线诊断工具 | 阿里开源，GitHub 35k+ Star |
| **OpenTelemetry Java Agent** | 可观测性标准实现 | CNCF 顶级项目 |
| **JaCoCo** | 代码覆盖率 | 测试领域标配 |
| **JRebel** | 热部署 | 商业产品，几乎每个 Java 团队都用过 |
| **IntelliJ IDEA Debugger** | 热替换调试 | 每个 Java 开发者日常使用 |

---

## 2. JVM Instrumentation 核心原理

### 2.1 Instrumentation 接口

JDK 1.5 引入了 `java.lang.instrument` 包（JEP 174）。核心接口 `Instrumentation` 提供了以下能力：

```java
public interface Instrumentation {
    // 注册 Class 文件转换器，每个类加载时都会触发
    void addTransformer(ClassFileTransformer transformer, boolean canRetransform);
    
    // 移除转换器
    boolean removeTransformer(ClassFileTransformer transformer);
    
    // 类加载后重新触发转换过程（不会修改已有的字段/方法签名）
    void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;
    
    // 直接替换类字节码（更严格，限制同 retransform）
    void redefineClasses(ClassDefinition... definitions)
        throws ClassNotFoundException, UnmodifiableClassException;
    
    // 获取 JVM 中所有已加载的类
    @SuppressWarnings("rawtypes")
    Class[] getAllLoadedClasses();
    
    // 获取已由 loader 加载的类
    @SuppressWarnings("rawtypes")
    Class[] getInitiatedClasses(ClassLoader loader);
    
    // 估算对象占用的内存大小（近似）
    long getObjectSize(Object objectToSize);
    
    // 是否支持 retransform
    boolean isRetransformClassesSupported();
    
    // 是否支持 redefine
    boolean isRedefineClassesSupported();
    
    // 判断类是否可修改
    boolean isModifiableClass(Class<?> theClass);
}
```

### 2.2 ClassFileTransformer 机制

`ClassFileTransformer` 是 Agent 的**核心工作接口**：

```java
public interface ClassFileTransformer {
    byte[] transform(
        ClassLoader loader,           // 正在加载该类的 ClassLoader
        String className,             // 类名（斜线格式：com/example/MyClass）
        Class<?> classBeingRedefined, // null=新类加载, 非null=retransform/redefine
        ProtectionDomain protectionDomain,
        byte[] classfileBuffer        // 原始字节码（不要直接修改此数组！）
    );
    // 返回 null = 不对该类做修改
    // 返回 byte[] = 用此字节码替换原始类
}
```

**关键行为：**
- **调用时机**：每个类在**被定义到 JVM 之前**触发（包括类加载、redefine、retransform）
- **不可变性**：`classfileBuffer` 是原始字节码，**禁止直接修改该数组**，必须拷贝后修改
- **null 语义**：返回 `null` 表示不修改；返回空数组或无效字节码会导致 `ClassFormatError`
- **异常安全**：`transform` 中抛出的异常会被 JVM 吞掉（该类的加载/转换会失败！）

### 2.3 类加载的生命周期拦截

```
JVM 类加载流程（被 Agent 介入后）：
┌────────────────────────────────────────────────────────────┐
│ 1. JVM 从字节码/class 文件读取原始二进制数据               │
│                                                             │
│ 2. addTransformer 注册的转换器被依次调用                     │
│    ┌─────────────────────────────────────────────┐         │
│    │ Transformer1 → Transformer2 → ... → null?   │         │
│    │ 每个返回 byte[] 的转换器，其结果成为下一个的输入       │
│    └─────────────────────────────────────────────┘         │
│                                                             │
│ 3. 最终的字节码交给 JVM 验证 → 准备 → 解析 → 初始化        │
│                                                             │
│ 4. 类被定义到方法区，可以被实例化了                          │
└────────────────────────────────────────────────────────────┘
```

> **⚠️ 重要限制**：`transform` 方法中**不能使用反射**来访问被转换类的成员，因为此时该类尚未被 JVM 完全定义。

---

## 3. 两种 Agent 模式：Premain vs Agentmain

### 3.1 Premain：启动时静态挂载

**适用场景**：需要在应用启动时就生效的场景（APM、安全审计、代码覆盖率）。

**META-INF/MANIFEST.MF 配置：**
```properties
Premain-Class: com.example.MyAgent
Can-Redefine-Classes: true
Can-Retransform-Classes: true
Can-Set-Native-Method-Prefix: true
```

**Agent 代码：**
```java
public class MyAgent {
    // 推荐写法：带 Instrumentation 参数
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("[Agent] premain called with args: " + agentArgs);
        inst.addTransformer(new MyTransformer(), true);
    }
    
    // 回退写法：如果上面的声明不存在，JVM 会查找这个签名
    public static void premain(String agentArgs) {
        // 此时无法获取 Instrumentation 实例，能力有限
    }
}
```

**启动命令：**
```bash
# 无参数
java -javaagent:myagent.jar -jar app.jar

# 带参数
java -javaagent:myagent.jar=debug=true,filter=com.example -jar app.jar

# 多个 Agent（按顺序执行）
java -javaagent:agent1.jar -javaagent:agent2.jar -jar app.jar
```

**执行顺序：**
```
JVM 初始化 → Agent.premain() → 应用的 main() 方法
```

### 3.2 Agentmain：运行时动态 Attach

**适用场景**：生产环境热修复、Arthas 式动态诊断、临时排查问题。

**MANIFEST.MF 配置：**
```properties
Agent-Class: com.example.DynamicAgent
Can-Redefine-Classes: true
Can-Retransform-Classes: true
```

**Agent 代码：**
```java
public class DynamicAgent {
    public static void agentmain(String agentArgs, Instrumentation inst) {
        System.out.println("[Agent] agentmain called, attaching to running JVM");
        inst.addTransformer(new MyTransformer(), true);
        
        // 对已加载的类立即执行 retransform
        try {
            inst.retransformClasses(TargetClass.class);
        } catch (UnmodifiableClassException e) {
            System.err.println("Failed to retransform: " + e.getMessage());
        }
    }
}
```

### 3.3 Attach API 详解

Attach API（`com.sun.tools.attach`）允许在运行时加载 Agent 到一个**正在运行的 JVM**：

```java
import com.sun.tools.attach.VirtualMachine;

public class AgentAttacher {
    public static void main(String[] args) throws Exception {
        // 1. 获取目标 JVM 的 PID（可以用 jps -l 命令查看）
        String targetPid = args[0];
        
        // 2. Attach 到目标 JVM
        VirtualMachine vm = VirtualMachine.attach(targetPid);
        
        try {
            // 3. 加载 Agent（第二个参数是传给 agentmain 的字符串参数）
            vm.loadAgent("/path/to/dynamic-agent.jar", "debug=true");
            
            // 4. 也可以加载本地的 Agent（不需要 JAR 文件）
            // vm.loadAgentLibrary("agentlib");
            // vm.loadAgentPath("/path/to/agent.so");
            
            System.out.println("[Attacher] Agent loaded successfully");
        } finally {
            // 5. Detach
            vm.detach();
        }
    }
}
```

**实战技巧：**
```bash
# 找到目标 JVM PID
jps -l

# 输出示例：
# 12345 myapp.jar
# 12346 sun.tools.jps.Jps

# Attach 执行
java -cp .:tools.jar AgentAttacher 12345
```

> **⚠️ 注意**：`tools.jar` 在 JDK 9+ 中被模块化，需要用 `--add-modules jdk.attach`。`VirtualMachine` 的类名不是标准 API，Oracle JDK 和 OpenJDK 均有，但 IBM J9 等不同。

---

## 4. 手写第一个 Java Agent（ASM 方式）

让我们从头构建一个完整的 Agent，给目标类的每个方法添加进入日志。

### 项目结构

```
my-first-agent/
├── pom.xml
├── src/main/java/
│   └── com/example/agent/
│       ├── SimpleAgent.java           # Agent 入口
│       └── LogMethodTransformer.java  # 字节码转换器
└── src/main/resources/
    └── META-INF/
        └── MANIFEST.MF                # Agent 清单
```

### Step 1: MANIFEST.MF

```properties
Premain-Class: com.example.agent.SimpleAgent
Can-Redefine-Classes: true
Can-Retransform-Classes: true
```

### Step 2: Agent 入口类

```java
package com.example.agent;

import java.lang.instrument.Instrumentation;

public class SimpleAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("[Agent] Hello from premain! args: " + agentArgs);
        inst.addTransformer(new LogMethodTransformer(), true);
    }
}
```

### Step 3: ASM Transformer

ASM 是底层字节码操作框架，采用**访问者模式**（类似 SAX 解析 XML）：

```java
package com.example.agent;

import org.objectweb.asm.*;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.security.ProtectionDomain;

public class LogMethodTransformer implements ClassFileTransformer {
    
    // 只拦截 com.example 包下的类
    private static final String TARGET_PREFIX = "com/example/";
    
    @Override
    public byte[] transform(ClassLoader loader, String className,
                           Class<?> classBeingRedefined,
                           ProtectionDomain protectionDomain,
                           byte[] classFileBuffer) {
        
        if (className == null) return null;
        if (!className.startsWith(TARGET_PREFIX)) return null;
        // 跳过接口、注解、枚举等
        if (classBeingRedefined != null && !canRetransform(classBeingRedefined)) return null;
        
        try {
            ClassReader cr = new ClassReader(classFileBuffer);
            ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_FRAMES);
            cr.accept(new ClassVisitor(Opcodes.ASM9, cw) {
                @Override
                public MethodVisitor visitMethod(int access, String name, String desc,
                                                String signature, String[] exceptions) {
                    MethodVisitor mv = super.visitMethod(access, name, desc, signature, exceptions);
                    // 跳过构造器和静态初始化块
                    if (name.equals("<init>") || name.equals("<clinit>")) {
                        return mv;
                    }
                    // 跳过 native 方法
                    if (Opcodes.ACC_NATIVE != 0 && (access & Opcodes.ACC_NATIVE) != 0) {
                        return mv;
                    }
                    return new MethodVisitor(Opcodes.ASM9, mv) {
                        @Override
                        public void visitCode() {
                            // 在方法体开头插入：
                            // System.out.println("[Agent] Entering: " + className + "." + name);
                            mv.visitFieldInsn(Opcodes.GETSTATIC, "java/lang/System",
                                "out", "Ljava/io/PrintStream;");
                            mv.visitLdcInsn("[Agent] Entering: " + className + "." + name);
                            mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/io/PrintStream",
                                "println", "(Ljava/lang/String;)V", false);
                            super.visitCode();
                        }
                    };
                }
            }, ClassReader.EXPAND_FRAMES);
            return cw.toByteArray();
        } catch (Exception e) {
            System.err.println("[Agent] Transform failed for " + className + ": " + e);
            return null; // 返回 null，保留原始字节码
        }
    }
    
    private boolean canRetransform(Class<?> clazz) {
        return !clazz.isInterface() && !clazz.isAnnotation() && !clazz.isEnum();
    }
}
```

### Step 4: Maven 打包配置

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-jar-plugin</artifactId>
      <version>3.3.0</version>
      <configuration>
        <archive>
          <manifestEntries>
            <Premain-Class>com.example.agent.SimpleAgent</Premain-Class>
            <Can-Redefine-Classes>true</Can-Redefine-Classes>
            <Can-Retransform-Classes>true</Can-Retransform-Classes>
          </manifestEntries>
        </archive>
      </configuration>
    </plugin>
    <!-- 用 maven-shade-plugin 将 ASM 依赖打包进 Agent JAR -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-shade-plugin</artifactId>
      <version>3.5.0</version>
      <executions>
        <execution>
          <goals><goal>shade</goal></goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>

<dependencies>
  <dependency>
    <groupId>org.ow2.asm</groupId>
    <artifactId>asm</artifactId>
    <version>9.7.1</version>
  </dependency>
</dependencies>
```

### Step 5: 运行测试

```bash
# 打包
mvn clean package

# 运行应用并挂载 Agent
java -javaagent:target/my-first-agent-1.0.jar -jar your-app.jar
```

---

## 5. 三大字节码框架选型

手写 ASM 强大但不友好。社区有三个主流框架，各有千秋：

### 5.1 ASM：底层性能王者

**由谁维护**：OW2 组织，已稳定发展 20+ 年。

**特点：**
- 直接操作 JVM 指令，**零抽象开销**
- 访问者模式，**内存友好**（无需加载完整类结构到内存）
- Spring、Hibernate、Gradle 等众多框架底层都在用
- **学习曲线陡峭**：需要理解 JVM 指令集、操作数栈、帧等概念

**典型示例——插入方法计时：**
```java
// ASM 方式
MethodVisitor mv = cv.visitMethod(access, name, desc, null, null);
mv.visitCode();
mv.visitMethodInsn(Opcodes.INVOKESTATIC, "java/lang/System",
    "nanoTime", "()J", false);
mv.visitVarInsn(Opcodes.LSTORE, maxLocals + 1);
// ... 原始方法代码 ...
mv.visitMethodInsn(Opcodes.INVOKESTATIC, "java/lang/System",
    "nanoTime", "()J", false);
mv.visitVarInsn(Opcodes.LLOAD, maxLocals + 1);
mv.visitInsn(Opcodes.LSUB);
// 记录耗时
```

**适用场景**：性能敏感的 APM Agent、框架底层、需要精细控制字节码的场景。

### 5.2 Javassist：字符串模板为王

**由谁维护**：JBoss（Red Hat），原东京工业大学研究项目。

**特点：**
- **直接用 Java 源码字符串**操作字节码，门槛最低
- 编译原理：Javassist 内部有 Java 源码编译器，`insertBefore("...")` 中的代码会被编译为字节码
- **性能比 ASM 略差**：因为需要源码编译、`CtClass` 会加载完整类结构到内存
- 不适合超高吞吐的场景

**完整示例——方法与上文 ASM 相同功能：**
```java
public class JavassistTransformer implements ClassFileTransformer {
    @Override
    public byte[] transform(ClassLoader loader, String className,
                           Class<?> beingRedefined,
                           ProtectionDomain pd, byte[] classfileBuffer) {
        if (className == null || !className.startsWith("com/example/")) return null;
        try {
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.makeClass(new ByteArrayInputStream(classfileBuffer));
            for (CtMethod method : ctClass.getDeclaredMethods()) {
                if (method.isEmpty()) continue; // abstract / native
                method.insertBefore(
                    "System.out.println(\"[Agent] Entering: " + method.getLongName() + "\");"
                );
                method.insertAfter(
                    "System.out.println(\"[Agent] Exiting: " + method.getLongName() + "\");",
                    true // 在 finally 块中插入，确保异常路径也能执行
                );
            }
            byte[] result = ctClass.toBytecode();
            ctClass.detach(); // 重要！释放内存
            return result;
        } catch (Exception e) {
            return null;
        }
    }
}
```

> **💡 实战注意**：`ClassPool.getDefault()` 在服务端容器（Tomcat、Jetty）中经常出问题，因为它使用 JVM 的 boot classpath 搜索类。建议用 `ClassPool(true)` 然后手动添加 classpath。更好的做法是用 `pool.appendClassPath(new LoaderClassPath(loader))` 传入目标类的 ClassLoader。

### 5.3 Byte Buddy：现代声明式 API

**由谁维护**：Rafael Winterhalter（核心作者），Netty 等项目的依赖。

**特点：**
- **声明式 API**：`ElementMatchers` + `Advice` 模式，代码可读性极强
- **自动类型解析**：自动处理 ClassLoader 问题，分析类型层次结构
- **内置 AgentBuilder**：专为 Agent 场景打造，支持原生配置、过滤、监听器
- **性能接近 ASM**（底层就是 ASM），抽象层开销极低

**完整 Agent 示例：**
```java
import net.bytebuddy.agent.builder.AgentBuilder;
import net.bytebuddy.asm.Advice;
import net.bytebuddy.matcher.ElementMatchers;
import java.lang.instrument.Instrumentation;

public class ByteBuddyAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        new AgentBuilder.Default()
            // 只处理 com.example 包
            .type(ElementMatchers.nameStartsWith("com.example"))
            // 忽略 Agent 自身的类（避免循环处理）
            .ignore(ElementMatchers.nameStartsWith("com.example.agent"))
            .transform((builder, type, cl, module) -> builder
                .visit(Advice.to(MethodTimer.class)
                    .on(ElementMatchers.isMethod()
                        .and(ElementMatchers.not(ElementMatchers.isConstructor()))
                        .and(ElementMatchers.not(ElementMatchers.isNative())))))
            .with(AgentBuilder.Listener.StreamWriting.toSystemOut())
            .installOn(inst);
    }
    
    // Advice 类：定义"在哪里插入什么代码"
    public static class MethodTimer {
        @Advice.OnMethodEnter
        public static long enter(@Advice.Origin("#t.#m") String method) {
            System.out.println("[Agent] Entering: " + method);
            return System.nanoTime();
        }
        
        @Advice.OnMethodExit(onThrowable = Throwable.class)
        public static void exit(@Advice.Origin("#t.#m") String method,
                                @Advice.Enter long startNanos,
                                @Advice.Thrown Throwable thrown) {
            long elapsed = System.nanoTime() - startNanos;
            System.out.println("[Agent] " + method + " took " + (elapsed / 1_000_000) + "ms"
                + (thrown != null ? " [thrown: " + thrown.getClass().getSimpleName() + "]" : ""));
        }
    }
}
```

**Byte Buddy 核心注解速查：**

| 注解 | 位置 | 作用 |
|------|------|------|
| `@Advice.OnMethodEnter` | 方法 | 方法进入时执行 |
| `@Advice.OnMethodExit` | 方法 | 方法退出时执行（含异常） |
| `@Advice.Origin` | 参数 | 注入原方法信息，支持占位符 `#t`/`#m`/`#r` |
| `@Advice.AllArguments` | 参数 | 注入所有参数 |
| `@Advice.Argument(n)` | 参数 | 注入第 n 个参数 |
| `@Advice.Return` | 参数 | 注入返回值（exit 方法） |
| `@Advice.Thrown` | 参数 | 注入抛出的异常（exit 方法） |
| `@Advice.Enter` | 参数 | 注入 enter 方法的返回值 |
| `@Advice.This` | 参数 | 注入当前对象（this） |

### 5.4 选型对比表

| 维度 | ASM | Javassist | Byte Buddy |
|------|:---:|:---------:|:----------:|
| **上手难度** | ⚠️ 高 | ✅ 低 | ✅ 低 |
| **性能** | 🏆 最高 | ⚠️ 中 | ✅ 很高 |
| **内存占用** | 🏆 最低 | ⚠️ 较高 | ✅ 低 |
| **代码可读性** | ❌ 差 | ⚠️ 一般 | 🏆 好 |
| **ClassLoader 处理** | 需要手动 | 需注意 ClassPool | ✅ 自动处理 |
| **Agent 支持** | 原生 | 原生 | ✅ AgentBuilder |
| **类型层次分析** | 手动 | 手动 | ✅ 自动 |
| **热部署/retransform** | 手动处理 | 需注意 | ✅ 内置支持 |
| **社区活跃度** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐✨ |
| **最佳场景** | APM 内核、框架底层 | 快速原型、简单增强 | 生产 Agent、复杂场景 |

> **结论**：大多数生产项目推荐 **Byte Buddy**；性能敏感的底层模块用 **ASM**；快速原型用 **Javassist**。

---

## 6. 实战案例：构建方法耗时监控 Agent

结合前三节的知识，构建一个完整的生产级耗时监控 Agent。

### 需求
- 监控指定包下的所有 public 方法耗时
- 支持慢方法阈值配置（超过多少 ms 输出警告）
- 支持排除指定方法名
- 可通过 agentArgs 传参配置

### 实现（Byte Buddy）

```java
public class PerfMonitorAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        // 解析配置
        PerfConfig config = PerfConfig.parse(agentArgs);
        
        new AgentBuilder.Default()
            .type(ElementMatchers.nameStartsWith(config.getTargetPackage()))
            .ignore(ElementMatchers.nameStartsWith("com.example.agent"))
            .transform((builder, type, cl, module) -> builder
                .visit(Advice.to(PerfAdvice.class)
                    .on(ElementMatchers.isPublic()
                        .and(ElementMatchers.not(ElementMatchers.isConstructor()))
                        .and(ElementMatchers.not(ElementMatchers.nameMatches(
                            String.join("|", config.getExcludeMethods())))))))
            .with(new AgentBuilder.Listener() {
                @Override public void onTransformation(TypeDescription td, ClassLoader cl,
                    JavaModule module, boolean loaded, DynamicType dynamicType) {
                    System.out.println("[PerfAgent] Instrumented: " + td.getName());
                }
                @Override public void onError(String typeName, ClassLoader cl,
                    JavaModule module, boolean loaded, Throwable throwable) {
                    System.err.println("[PerfAgent] Error: " + typeName + " - " + throwable);
                }
                @Override public void onIgnored(TypeDescription td, ClassLoader cl,
                    JavaModule module, boolean loaded) {}
                @Override public void onComplete(String typeName, ClassLoader cl,
                    JavaModule module, boolean loaded) {}
            })
            .installOn(inst);
    }
    
    public static class PerfAdvice {
        @Advice.OnMethodEnter
        public static long enter() {
            return System.nanoTime();
        }
        
        @Advice.OnMethodExit(onThrowable = Throwable.class)
        public static void exit(@Advice.Origin("#t.#m") String method,
                                @Advice.Enter long startTime,
                                @Advice.Thrown Throwable thrown) {
            long costMs = (System.nanoTime() - startTime) / 1_000_000;
            if (costMs > PerfConfig.getSlowThresholdMs()) {
                System.err.println("[PERF_WARN] " + method + " took " + costMs + "ms (slow!)"
                    + (thrown != null ? " !!Exception: " + thrown.getClass().getName() : ""));
            }
            // 所有方法记录到 metrics
            PerfMetrics.record(method, costMs, thrown != null);
        }
    }
    
    static class PerfConfig {
        // 默认配置
        private static int slowThresholdMs = 1000;
        private static String targetPackage = "com.example";
        private static List<String> excludeMethods = Arrays.asList("toString", "hashCode", "equals");
        
        public static PerfConfig parse(String args) {
            if (args == null || args.isEmpty()) return new PerfConfig();
            // 解析 arg 格式：package=com.example;threshold=500;exclude=toString,hashCode
            for (String pair : args.split(";")) {
                String[] kv = pair.split("=", 2);
                if (kv.length != 2) continue;
                switch (kv[0]) {
                    case "package": targetPackage = kv[1]; break;
                    case "threshold": slowThresholdMs = Integer.parseInt(kv[1]); break;
                    case "exclude": excludeMethods = Arrays.asList(kv[1].split(",")); break;
                }
            }
            return new PerfConfig();
        }
        
        public static int getSlowThresholdMs() { return slowThresholdMs; }
        public String getTargetPackage() { return targetPackage; }
        public List<String> getExcludeMethods() { return excludeMethods; }
    }
}
```

### 用法

```bash
# 默认配置（com.example 包，1s 阈值）
java -javaagent:perf-agent.jar -jar app.jar

# 自定义配置
java -javaagent:perf-agent.jar="package=com.myapp;threshold=200;exclude=toString,hashCode,getter" -jar app.jar
```

---

## 7. 生产级最佳实践

### 7.1 性能优化

**1. XTransformer 处理速度必须极快**

`transform` 方法在类加载路径上——它慢，你的应用就慢。关注点：

```java
// ❌ 错误：每次都做重量级操作
if (classFileBuffer.length > 10_000) { ... } // 无条件读取

// ✅ 正确：先做快速过滤，再处理具体类
if (!className.startsWith("com/example/")) return null; // 99% 的类在这里就不处理了
```

**2. 缓存已处理的字节码**

Java Agent 在处理大型类时，相同类名只会加载一次。但如果使用 retransform，需要避免重复处理：

```java
// 最佳实践：用 ConcurrentHashMap 记录已处理的类
private static final ConcurrentHashMap<String, Boolean> processed = new ConcurrentHashMap<>();

public byte[] transform(...) {
    if (!className.startsWith("com/example/")) return null;
    // 如果已处理过且不是 retransform 触发，跳过
    if (processed.putIfAbsent(className, Boolean.TRUE) != null 
        && classBeingRedefined == null) {
        return null;
    }
    // ... 实际的转换逻辑
}
```

**3. 避免反射调用**

在被增强的方法中使用反射（如 `Method.invoke()`）会比直接方法调用慢 2-5 倍：

```java
// ❌ 慢：反射调用
method.invoke(obj, args);

// ✅ 快：直接 invokevirtual（ASM 生成的调用）
mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, ...);
```

**4. 选择合适 ClassWriter 模式**

```java
// ❌ COMPUTE_FRAMES 最省事，但最慢
ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_FRAMES);

// ✅ COMPUTE_MAXS 更快（只要你的字节码框架不乱）
ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_MAXS);

// 🏆 最快（自己计算 max_stack / max_locals），但这几乎不可维护
ClassWriter cw = new ClassWriter(cr, 0);
```

> Byte Buddy 默认使用 `COMPUTE_MAXS` 模式。如果你的 Agent 以 Byte Buddy 为主，性能已经不错了。

**5. 减少被增强的方法数量**

不需要对所有方法都做增强：
- 跳过 getter/setter（它们通常很快）
- 跳过 `toString()`、`hashCode()`、`equals()`
- 跳过 JDK 自带类（除非必要）
- 用 `ElementMatchers` 精确匹配

### 7.2 安全与稳定性

**1. 幂等性——重复增强必须安全**

如果 Agent 被重复 attach（比如热部署时），或者多个 Agent 增强同一个方法，必须保证幂等：

```java
// ❌ 危险：每次 retransform 都会添加一次 System.out.println
method.insertBefore("System.out.println(\"Entering method\");");

// ✅ 安全：先检查是否已增强（通过添加自定义注解或标记字段）
// Javassist 示例：
CtMethod m = ctClass.getDeclaredMethod(methodName);
if (m.getAnnotation(AlreadyInstrumented.class) == null) {
    m.insertBefore("System.out.println(\"Entering method\");");
    // 添加标记
    // 但 Javassist 不能直接给方法加注解（受限制），变通方案用字段标记
}
```

**更好的方案**：在 `ClassFileTransformer` 中维护一个 `Set<String>` 记录已处理的类，返回 `null` 跳过已处理过的。

**2. 异常绝不能逃逸**

`transform` 中抛出的异常会被 JVM 捕获并导致该类加载失败（或 `retransform` 失败）：

```java
// ❌ 错误：unchecked exception 会导致类加载失败
public byte[] transform(...) {
    int x = 1 / 0; // ArithmeticException! 目标应用直接崩
}

// ✅ 正确：任何异常都要 catch，返回 null 保证安全
public byte[] transform(...) {
    try {
        // ... transform logic
    } catch (Exception e) {
        System.err.println("[Agent] Error transforming " + className + ": " + e);
        return null; // 返回 null，保留原始字节码
    }
}
```

> **💡 特别注意**：`ClassFormatError` 在低版本 JDK（<= 8）中可能不会触发 `catch(Exception)`——它继承自 `Error`。建议同时 catch `Throwable` 或 `Error`。

**3. 绝不修改核心 JDK 类**

永远不要在 Agent 中修改以下类：
- `java.lang.String`、`java.lang.Object`
- `java.lang.ClassLoader`（及其子类）
- `java.lang.Thread`
- `java.lang.System`
- `java.util.*` 中的核心集合类
- `java.lang.reflect.*`

**原因**：这些类在 JVM 启动初期就被使用，JVM 对它们有特殊的初始化顺序。修改它们可能导致不可预知的崩溃，甚至 JVM native crash（`hs_err_pid*.log`）。

**4. 考虑 Java 模块系统（JPMS）**

JDK 9+ 引入了模块系统，Agent 需要额外配置：

```java
// 在 MANIFEST.MF 中声明
Can-Retransform-Classes: true
Can-Redefine-Classes: true

// 同时可能需要添加 JVM 启动参数：
// --add-opens java.base/java.lang=ALL-UNNAMED
```

**5. 避免使用 `sun.*` 内部 API**

不要依赖 `sun.misc.*`、`sun.reflect.*` 等——它们在 JDK 9+ 中被移除或模块化。使用标准 `java.lang.instrument` API。

### 7.3 兼容性

**1. 测试所有目标 JVM 版本**

字节码格式在不同 JDK 版本间有细微差异：

| JDK | 关键变化 | 对 Agent 的影响 |
|-----|---------|----------------|
| Java 8 | 默认 stack map frames | COMPUTE_FRAMES 必须支持 |
| Java 9 | 模块系统 + 新 class 文件版本 53 | `--add-opens` |
| Java 11 | Nest-based access（新访问控制） | ASM 6+ required |
| Java 14 | Records + Pattern Matching | ASM 8+ required |
| Java 16 | Records 增强 + sealed classes | ASM 9+ required |
| Java 17+ | 封装内部 API | `--add-opens` 配置 |
| Java 21 | Virtual Threads | Agent 栈帧处理需注意 |

**建议**：使用 `ASM 9.7+` + `Byte Buddy 1.15+` 覆盖 Java 8~21。

**2. 非 Oracle JDK 的差异**

- **IBM J9 / OpenJ9**：部分 `Instrumentation` 方法行为不同
  - `retransformClasses()` 可能不支持（抛 `UnsupportedOperationException`）
  - `getObjectSize()` 实现不同
- **GraalVM Native Image**：**不支持** Java Agent（AOT 编译，无字节码）
- **Android ART**：不是标准 JVM，**不支持** `java.lang.instrument`

**3. 容器环境中的问题**

Docker/K8s 容器化场景：
- **PID 1 问题**：如果 Java 进程是容器 PID 1，`VirtualMachine.attach()` 可能会失败
  - 原因：PID 1 没有处理 SIGQUIT 的能力（`VirtualMachine` 的 attach 行为）
  - 解决：用 `tini` 或 `dumb-init` 作为容器入口
- **资源限制**：Agent 的启动类变换会占用额外 CPU（尤其在 K8s 的 CPU limit 下）

### 7.4 包冲突与 Shade 技术

**这是 Java Agent 生产部署中最常见的坑。**

### 问题

你的 Agent JAR 里的 ASM 版本（比如 9.7），和目标应用的依赖中 ASM 版本（比如 9.2）冲突。更糟糕——如果 Agent 依赖了 Guava、Netty 等通用库，和目标应用的版本不同，轻则 `NoSuchMethodError`，重则 JVM crash。

### 解决方案：Maven Shade + 包重定位

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.0</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>shade</goal></goals>
            <configuration>
                <!-- 重定位：将 Agent 内部的 ASM 包名改掉 -->
                <relocations>
                    <relocation>
                        <pattern>org.objectweb.asm</pattern>
                        <shadedPattern>com.example.agent.shaded.asm</shadedPattern>
                    </relocation>
                    <relocation>
                        <pattern>net.bytebuddy</pattern>
                        <shadedPattern>com.example.agent.shaded.bytebuddy</shadedPattern>
                    </relocation>
                </relocations>
                <!-- 确保 Agent 自身类不冲突（保留原始包名） -->
                <filters>
                    <filter>
                        <artifact>*:*</artifact>
                        <excludes>
                            <exclude>META-INF/versions/**</exclude>
                        </excludes>
                    </filter>
                </filters>
            </configuration>
        </execution>
    </executions>
</plugin>
```

> **What this does**：`org.objectweb.asm.SomeClass` 在 Agent JAR 中变成 `com.example.agent.shaded.asm.SomeClass`。目标应用的 classpath 上有旧版本 ASM 也完全不影响，因为包名不同。

---

## 8. 血泪踩坑实录

### 8.1 ClassLoader 地狱

**现象**：Agent 运行时出现 `ClassNotFoundException` 或 `NoClassDefFoundError`。

**根因**：你的 Transformer 代码（比如 Javassist 生成的字节码中引用了 `com.example.SomeUtil`）运行在**目标类的 ClassLoader** 下，而不是 Agent 的 ClassLoader。

```
┌─ 场景 ─────────────────────────────────────────────────┐
│                                                        │
│ App Server (Tomcat)                                    │
│  ├── Common ClassLoader (容器共享库)                    │
│  ├── WebApp1 ClassLoader → 加载了 com.example.service  │
│  ├── WebApp2 ClassLoader → 加载了 com.example.service  │
│  └── Agent 的 Transformer 运行在哪个 ClassLoader 下？  │
│                                                        │
│ 答案：每个类各自的 ClassLoader！                          │
│ 你注入的代码中调用 UserService → 找不到（因为在不同的   │
│ ClassLoader 里）                                        │
└────────────────────────────────────────────────────────┘
```

**解决方案：**
1. **用 boot classpath 加载 Agent 辅助类**（javassist、byte-buddy 等库）
2. **优先使用字节码指令**而不是反射调用
3. **将辅助类放到 bootstrap classloader 作用域**（`-Xbootclasspath/a:helper.jar`）
4. Byte Buddy 的 Advice 已经处理了 ClassLoader 问题，优先使用

```java
// ❌ 会出问题：注入的代码中调用了 Agent 侧的类
method.insertBefore("com.example.agent.Helper.startTimer();");

// ✅ 安全的做法：用字节码直接注入 System.out/System.nanoTime() 等 JDK 类方法
// 因为 java.lang.System 由 Bootstrap ClassLoader 加载，所有 ClassLoader 可见
method.insertBefore("System.nanoTime();");
```

### 8.2 核心 JDK 类篡改的灾难

**现象**：JVM 启动几分钟后突然 Native Crash（`hs_err_pid*.log`），没有 Java 异常栈。

**根因**：Agent 误改了 `java.lang.String`、`java.util.HashMap` 等核心类，导致 JVM 内部数据结构损坏。

**案例**：某团队在 Agent 中给 `String` 的所有方法加了日志，结果——`String.intern()` 的 intern 表中插入了日志字符串，导致永久代（PermGen / Metaspace）撑爆。

> **铁律**：如果你在写通用 Agent（不是专门调试 String 本身），`String`、`Object`、`ClassLoader` 等以 `java.` 开头的类一律跳过。

### 8.3 重入变换与栈溢出

**现象**：Agent 运行后应用栈溢出（`StackOverflowError`）。

**根因**：Transformer 中引用了自身要增强的类，导致无限递归。

```java
// ❌ 经典错误
public byte[] transform(... className) {
    // 处理所有 com.example 包下的类
    if (className.startsWith("com/example/")) {
        // 给方法加日志
        // ...
        // 但：这个 Transformer 类本身也在 com.example 包下！
        // 当 JVM 第一次加载 Transformer 时会再次触发 transform
        // Transformer 又引用了 Myservice → 又触发 transform → ∞
    }
}
```

**解决方案：**
- 始终过滤掉 Agent 自身的包
- 使用 `ElementMatchers.nameStartsWith("com.example").and(ElementMatchers.not(nameStartsWith("com.example.agent")))`
- 在 Byte Buddy 的 `AgentBuilder.Default()` 中使用 `.ignore()` 方法

### 8.4 启动耗时爆炸

**现象**：加上 Agent 后，应用启动时间从 30 秒变成 5 分钟。

**根因**：Agent 在启动阶段对所有类的 `transform` 都是同步的。

**真实数据**（来自 Spring Boot + OpenTelemetry Agent）：
- 不加 Agent：启动 25s
- 加 OTel Agent（默认配置）：启动 160s（6-7x 变慢）
- 加优化配置（只增强需要的类）：启动 35s

**解决策略：**
1. **精确过滤**：只增强需要的类（包名前缀、注解匹配）
2. **延迟增强**：对非关键类，推迟到实际使用时再增强（Byte Buddy 的 `AgentBuilder` 支持）
3. **并行增强**：JDK 8+ 可以用 `RetransformManager` 并行处理
4. **缓存结果**：重复 retransform 时跳过
5. **预热**：在流量灰度前完成所有类的加载和增强

### 8.5 Metaspace 内存泄漏

**现象**：应用运行几小时后出现 `OutOfMemoryError: Metaspace`。

**根因**：每次 `retransform` / `redefine` 操作都会在 Metaspace 中保留原始类的元数据。在热重载场景（如 Spring DevTools、JRebel、或者频繁的 retransform 调用）中，旧的 Class 元数据无法被 GC。

**具体场景：**
- Arthas 频繁 watch/trace 同一个类 → 每次 retransform 产生新 Class 元数据
- 热部署 → 新的 ClassLoader 创建 + 旧的 ClassLoader 泄漏
- Agent 每次都在 `transform` 中返回**新的 byte[]**，JVM 每次会创建新的 Klass 结构

**解决方案：**
1. **不要频繁 retransform**：Class 一旦增强就保持不变
2. **使用 `-noverify` 减少元数据**（有安全风险，建议仅在测试环境）
3. **开启 Metaspace GC**：`-XX:+PrintMetaspaceStatistics` 监控 Metaspace 使用
4. **多 ClassLoader 环境下**：确保 Agent 不会无限制地创建 ClassLoader
5. **Byte Buddy 的 `TypeStrategy.Default.REDEFINE`** 比默认策略更 Metaspace 友好

### 8.6 跨 JVM 版本的字节码兼容性

**现象**："Agent 在 Java 8 上跑得好好的，升级到 Java 17 后就崩了。"

**根因**：字节码格式变更。

**典型问题：**
1. **Java 9+ 的 Nest-Based Access**：之前合法的 `invokevirtual` 现在变成 `invokespecial`，ASM 6+ 才支持
2. **Java 11+ 的 Constant Dynamic**：lambda 表达式从 invokedynamic 改为 condy，影响 Transformer 对 lambda 的处理
3. **Java 16+ 的 sealed class 和 record**：`ClassWriter.COMPUTE_FRAMES` 在新的类格式下可能计算出错
4. **`native` 方法的 `Can-Set-Native-Method-Prefix`**：低版本 JVM 不支持

**解决方案：**
```xml
<!-- 使用最新的 ASM 和 Byte Buddy 版本 -->
<dependency>
    <groupId>org.ow2.asm</groupId>
    <artifactId>asm</artifactId>
    <version>9.7.1</version>  <!-- 覆盖 Java 8~21 -->
</dependency>
<dependency>
    <groupId>net.bytebuddy</groupId>
    <artifactId>byte-buddy</artifactId>
    <version>1.15.10</version> <!-- 1.14+ 支持 Java 21 -->
</dependency>
```

**最低版本对照：**
| 目标 JDK | 最低 ASM | 最低 Byte Buddy |
|---------|----------|----------------|
| Java 8 | 5.0+ | 0.6+ |
| Java 11 | 6.0+ | 1.9+ |
| Java 14 | 8.0+ | 1.10+ |
| Java 16 | 9.0+ | 1.11+ |
| Java 17 | 9.2+ | 1.12+ |
| Java 21 | 9.6+ | 1.14+ |

---

## 9. 工业级案例：OpenTelemetry Java Agent

**OpenTelemetry Java Agent** 是业界最成功的 Java Agent 之一，CNCF 顶级项目，Github 2k+ Stars。

### 架构概览

```
┌─────────────────────────────────────────┐
│ OpenTelemetry Java Agent                 │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Agent 启动层                      │   │
│  │  - 解析配置 (环境变量/系统属性)    │   │
│  │  - 初始化 SDK                    │   │
│  │  - 注册 ClassFileTransformer     │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ 字节码增强层                      │   │
│  │  - InstrumentationModule          │   │
│  │  - TypeInstrumentation            │   │
│  │  - Advice 类                     │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ 内置 Instrumentation 模块         │   │
│  │  ├── HTTP (Spring MVC, JAX-RS)   │   │
│  │  ├── Database (JDBC, R2DBC)      │   │
│  │  ├── Messaging (Kafka, JMS)      │   │
│  │  ├── gRPC / Netty / OkHttp       │   │
│  │  └── 50+ 框架                     │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 关键设计

1. **分层的 InstrumentationModule + TypeInstrumentation 模式**
   - 每个框架（Spring MVC、JDBC 等）是一个模块
   - 每个模块中可以增强多个"点"（如 `DispatcherServlet.doDispatch`）
   - 模块之间互相独立

2. **Advice 类隔离**
   - Agent 代码和目标应用代码**完全隔离**
   - Advice 被注入到目标应用中，但设计时确保仅调用 JDK 原生 API
   - Agent 的依赖（guava、gRPC 等）都通过 shading 重定位

3. **配置覆盖一切**（零代码改动原则）
   ```bash
   # 通过环境变量配置所有行为
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
   export OTEL_SERVICE_NAME=my-service
   export OTEL_TRACES_EXPORTER=otlp
   export OTEL_METRICS_EXPORTER=otlp
   export OTEL_LOGS_EXPORTER=none
   
   java -javaagent:opentelemetry-javaagent.jar -jar myapp.jar
   ```

### 踩坑经验：OpenTelemetry Agent 的 gotchas

来自社区和博客：[blog.frankel.ch/opentelemetry-gotchas](https://blog.frankel.ch/opentelemetry-gotchas/)

| 问题 | 表现 | 原因 |
|------|------|------|
| **启动慢** | Spring Boot 从 25s → 160s | 50+ 个 instrumentation 模块都要执行一次 |
| **日志不发送** | trace 正常但日志没到 collector | OTEL 日志默认关闭，需显式设置 `OTEL_LOGS_EXPORTER=otlp` |
| **endpoint 路径** | trace 发送到 `/v1/traces` 但 collector 401 | SDK 自动追加 `/v1/traces`，不需要在 endpoint 里写 |
| **Quarkus 不兼容** | Quarkus 的 OTel 用 `QUARKUS_OTEL_*` 前缀 | 非标准 prefix，运维人员容易忽略 |
| **Micrometer Tracing 冲突** | Meter 被双重收集 | Micrometer Tracing 的 endpoint 变量名不同 |

---

## 10. 诊断与调试工具链

### 诊断 Agent 问题

| 场景 | 工具/方法 | 说明 |
|------|----------|------|
| **Agent 是否加载成功** | `-XX:+TraceClassLoading` | 看 Agent 类是否被加载 |
| **类被哪些 Transformer 修改** | `-Djava.util.logging.config.file=...` | 开启 Agent 自身日志 |
| **字节码是否正确** | `javap -c -p ClassName` | 反编译查看生成的字节码 |
| **类的加载顺序** | `-verbose:class` / `-Xlog:class+load` (JDK 9+) | 看类加载时间线 |
| **谁在加载一个类** | `-XX:+TraceClassResolution` | 调试 ClassLoader 问题 |
| **Metaspace 使用** | `-XX:+PrintMetaspaceStatistics` | 监控 Metaspace 泄漏 |
| **retransform 是否成功** | `Instrumentation.isModifiableClass(clazz)` | 程序化检测 |

### 调试自己的 Transformer

```java
public class DebugTransformer implements ClassFileTransformer {
    private static final boolean DEBUG = Boolean.getBoolean("agent.debug");
    
    @Override
    public byte[] transform(...) {
        if (className == null) return null;
        
        long start = System.nanoTime();
        boolean modified = false;
        
        try {
            // 快速过滤
            if (!shouldTransform(className)) return null;
            
            if (DEBUG) {
                System.out.println("[Agent] Transforming: " + className
                    + " (loader=" + loader + ")");
            }
            
            // 实际转换
            byte[] result = doTransform(loader, className, classFileBuffer);
            modified = (result != null);
            return result;
        } catch (Throwable t) {
            // 关键：不放过任何异常
            System.err.println("[Agent] FATAL: transform failed for " + className);
            t.printStackTrace();
            return null; // 安全回退
        } finally {
            long elapsed = System.nanoTime() - start;
            if (DEBUG && modified) {
                System.out.println("[Agent] Transformed " + className
                    + " in " + (elapsed / 1_000_000) + "ms");
            }
        }
    }
}
```

### 生产环境排查

```bash
# 1. 检查 Agent 是否已加载
jcmd <PID> VM.system_properties | grep javaagent

# 2. 检查哪些 Agent 已注册
jcmd <PID> VM.command_line

# 3. 看哪个类加载器有问题
jcmd <PID> VM.classloader_stats

# 4. 强制触发 GC 看 Metaspace 释放情况
jcmd <PID> GC.heap_dump /tmp/dump.hprof
```

---

## 11. 总结

### 关键知识点回顾

1. **Java Agent ≠ 字节码操作框架**：Agent 是 JVM 的钩子机制，字节码操作是它的典型但不唯一的用途（也可以改环境变量、配置等）
2. **Premain vs Agentmain**：启动时挂载 vs 运行时 Attach，后者依赖 Attach API（`com.sun.tools.attach`）
3. **三大字节码框架**：ASM（高性能底层）、Javassist（源码字符串）、Byte Buddy（声明式现代 API）
4. **Shade 重定位是必选项**：否则 AGent 的依赖与目标应用冲突，`NoSuchMethodError` 接踵而至
5. **ClassLoader 是最深的水**：Agent 代码在目标类的 ClassLoader 下执行，bootstrap classpath 是最安全的位置
6. **永远不要修改 JDK 核心类**：String、Object、ClassLoader 等修改可能直接 JVM crash

### 生产级 Agent Checklist

```
□ 是否过滤了 Agent 自身的包防止重入？
□ 是否使用 Shade 重定位了所有第三方依赖？
□ transform 方法是否捕获了 Exception + Error？
□ 是否跳过了 JDK 核心类（java.*）？
□ 是否缓存了已处理的类防止幂等问题？
□ 是否在 Java 8/11/17/21 都测试通过？
□ 是否验证了多 ClassLoader 环境（Tomcat/Spring Boot DevTools）？
□ 是否考虑过 Metaspace 泄漏风险？
□ 是否监控了应用启动时间增加？
□ 是否需要处理容器 PID 1 的 Attach 问题？
```

### 一句话总结

> **Java Agent 是 JVM 生态中最强大的能力之一，但也是生产环境中最容易出问题的技术之一。框架选 Byte Buddy、用 Shade 做包隔离、跳过 JDK 核心类、对异常零容忍——做到这四点，你的 Agent 已经赢了 90% 的生产问题。**

---

## 参考资料

| 来源 | 链接 |
|------|------|
| Oracle 官方 API 文档 | [java.lang.instrument](https://docs.oracle.com/en/java/javase/17/docs/api/java.instrument/java/lang/instrument/package-summary.html) |
| Baeldung: Java Instrumentation 指南 | [baeldung.com/java-instrumentation](https://www.baeldung.com/java-instrumentation) |
| InfoQ: Byte Buddy Java Agent 指南 | [infoq.com/articles/Easily-Create-Java-Agents-with-ByteBuddy](https://www.infoq.com/articles/Easily-Create-Java-Agents-with-ByteBuddy/) |
| Medium: Java Agents & Bytecode Manipulation | [medium.com/javarevisited/...](https://medium.com/javarevisited/java-agents-bytecode-manipulation-made-easy-a-deep-dive-with-asm-and-bytebuddy-1c241cd158f4) |
| javathinking: Java Instrumentation 完全指南 | [javathinking.com/blog/guide-to-java-instrumentation](https://www.javathinking.com/blog/guide-to-java-instrumentation/) |
| OpenTelemetry Java Agent | [opentelemetry.io/docs/zero-code/java/agent](https://opentelemetry.io/docs/zero-code/java/agent/) |
| OpenTelemetry Java Agent 源码 | [github.com/open-telemetry/opentelemetry-java-instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation) |
| Byte Buddy 官方文档 | [bytebuddy.net](https://bytebuddy.net) |
| ASM 官方网站 | [asm.ow2.io](https://asm.ow2.io) |
| Javassist 官方文档 | [jboss-javassist.github.io/javassist](https://jboss-javassist.github.io/javassist) |
| OpenTelemetry Gotchas | [blog.frankel.ch/opentelemetry-gotchas](https://blog.frankel.ch/opentelemetry-gotchas/) |
