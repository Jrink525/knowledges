---
title: "Maven 完全教程：从入门到实践"
tags:
  - maven
  - java
  - build-tools
  - dependency-management
date: 2026-06-21
source: "https://jenkov.com/tutorials/maven/maven-tutorial.html"
authors: "Jakob Jenkov (原文) / 深度整理与补充"
---

# Maven 完全教程：从入门到实践

> **来源：** [Maven Tutorial - Jenkov.com](https://jenkov.com/tutorials/maven/maven-tutorial.html)  
> **版本基础：** Maven 3.6.3+ | **补充内容：** Maven 4.x 新特性、常见实践、最佳实践

---

## 一、Maven 是什么？

Maven 是 Apache 旗下的**项目管理与构建自动化工具**。它基于 **POM（Project Object Model）** 的声明式思想：你在 `pom.xml` 中**描述项目是什么**（依赖、结构、打包方式），而不是描述**怎么构建**。

Maven 的核心价值：

- **统一构建规范** — 标准化目录结构、生命周期、构建流程
- **自动依赖管理** — 自动下载依赖及其传递依赖，解决版本冲突
- **仓库机制** — 本地/中央/远程三级仓库
- **插件体系** — 通过 plugin 扩充任意构建功能
- **继承与聚合** — 多模块项目管理

### Maven 的核心哲学

> "Maven is more than just a build tool — it is a project management platform."

Maven 强调**约定优于配置**（Convention over Configuration）：只要你遵循默认的目录结构和命名规则，不需要写任何构建逻辑就能完成编译、测试、打包、部署。

---

## 二、安装与环境配置

### 前置条件

- **Java SDK**（不是 JRE）— Maven 本身就是 Java 程序，编译也需要 JDK
- **Java 版本兼容**：
  - Maven 3.3+ 需要 Java 7+
  - Maven 3.6+ 需要 Java 8+
  - Maven 4.x 需要 Java 17+

### 安装步骤

```bash
# 1. 设置 JAVA_HOME
export JAVA_HOME=/path/to/jdk

# 2. 下载并解压 Maven
wget https://dlcdn.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz
tar -xzf apache-maven-3.9.9-bin.tar.gz -C /opt/

# 3. 设置环境变量
export M2_HOME=/opt/apache-maven-3.9.9
export M2=$M2_HOME/bin
export PATH=$M2:$PATH

# 4. 验证
mvn -version
```

Windows 用户需设置 `%JAVA_HOME%`、`%M2_HOME%` 并将 `%M2%` 加入 `PATH`。

### 验证输出示例

```
Apache Maven 3.9.9 (8e8f0b9bdebc3a2c8e85f8b7e8b5c3c9f8b8e8f0)
Maven home: /opt/apache-maven-3.9.9
Java version: 21.0.2, vendor: Oracle Corporation, runtime: /opt/jdk-21
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "6.5.0", arch: "amd64"
```

---

## 三、核心概念全景

```
┌─────────────────────────────────────────────┐
│              Maven 核心体系                     │
│  ┌──────────┐   ┌──────────────────────┐     │
│  │  POM 文件 │──→│ 生命周期(Lifecycle)  │     │
│  └──────────┘   │  ├─ default          │     │
│       │         │  ├─ clean            │     │
│       │         │  └─ site             │     │
│       │         └──────────┬───────────┘     │
│       │                    ↓                  │
│       │         ┌──────────────────────┐     │
│       ├────────→│  阶段(Phase)          │     │
│       │         │  compile→test→pack...│     │
│       │         └──────────┬───────────┘     │
│       │                    ↓                  │
│       │         ┌──────────────────────┐     │
│       ├────────→│  目标(Goal)=Plugin    │     │
│       │         │  compiler:compile     │     │
│       │         │  surefire:test        │     │
│       │         └──────────────────────┘     │
│       │                                       │
│  ┌────┴──────┐  ┌──────────┐  ┌─────────┐    │
│  │  依赖管理  │  │ 仓库系统  │  │ 构建配置  │   │
│  │  scope    │  │ 本地+中央 │  │ profile │   │
│  │  transitive│  │ +远程    │  │ plugin  │   │
│  └───────────┘  └──────────┘  └─────────┘    │
└─────────────────────────────────────────────┘
```

---

## 四、POM 文件详解

### 4.1 最小 POM

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
</project>
```

### 4.2 GAV 坐标（Maven Coordinates）

每个项目由三个元素唯一定位，称为 **GAV**：

| 元素 | 含义 | 示例 | 映射到仓库路径 |
|------|------|------|---------------|
| `groupId` | 组织/项目唯一标识 | `com.example` | `com/example/` |
| `artifactId` | 项目名称 | `my-app` | `my-app/` |
| `version` | 版本号 | `1.0.0` | `1.0.0/` |

仓库中的完整路径：`~/.m2/repository/com/example/my-app/1.0.0/my-app-1.0.0.jar`

### 4.3 packaging 类型

```xml
<packaging>jar</packaging>   <!-- 默认值 -->
<packaging>war</packaging>   <!-- Web 应用 -->
<packaging>pom</packaging>   <!-- 父项目或多模块聚合 -->
<packaging>ear</packaging>   <!-- Enterprise Archive -->
<packaging>maven-plugin</packaging>
```

### 4.4 POM 继承（Super POM）

所有 POM 隐式继承自 Maven 内置的**超级 POM**（Super POM），其中定义了：

- 默认目录结构
- 中央仓库地址（`https://repo.maven.apache.org/maven2`）
- 默认插件版本和绑定
- 默认生命周期映射

查看有效 POM（Effective POM）：

```bash
mvn help:effective-pom
```

自定义父 POM：

```xml
<parent>
    <groupId>com.example</groupId>
    <artifactId>parent-project</artifactId>
    <version>1.0.0</version>
    <relativePath>../parent/pom.xml</relativePath>
</parent>
```

### 4.5 POM 常用元素一览

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    
    <!-- 坐标 -->
    <groupId>...</groupId>
    <artifactId>...</artifactId>
    <version>...</version>
    <packaging>jar</packaging>
    
    <!-- 项目信息 -->
    <name>My App</name>
    <description>...</description>
    <url>https://example.com</url>
    
    <!-- 属性（集中管理版本号等） -->
    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <!-- 依赖管理（锁定版本） -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>3.3.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    
    <!-- 实际依赖 -->
    <dependencies>
        ...
    </dependencies>
    
    <!-- 构建配置 -->
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
                <configuration>
                    <source>21</source>
                    <target>21</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
    
    <!-- Profiles -->
    <profiles>
        <profile>
            <id>production</id>
            ...
        </profile>
    </profiles>
</project>
```

---

## 五、依赖管理（Dependency Management）

### 5.1 基本声明

```xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter-api</artifactId>
        <version>5.11.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 5.2 依赖范围（Scope）

| Scope | 编译 | 测试 | 运行 | 说明 |
|-------|:----:|:----:|:----:|------|
| `compile`（默认） | ✅ | ✅ | ✅ | 所有阶段都可用 |
| `provided` | ✅ | ✅ | ❌ | 容器/JDK 已提供，如 Servlet API |
| `runtime` | ❌ | ✅ | ✅ | 编译不需要，运行时需要 |
| `test` | ❌ | ✅ | ❌ | 仅测试阶段 |
| `system` | ✅ | ✅ | ❌ | 显式指定本地路径，不通过仓库 |
| `import` | — | — | — | 仅用于 `dependencyManagement` 的 type=pom |

### 5.3 传递依赖（Transitive Dependencies）

Maven 会自动拉取依赖的依赖。例如：

```
项目 A 依赖 B
    B 依赖 C (compile)
        C 依赖 D (compile)
→ A 自动获得 B、C、D
```

### 5.4 依赖仲裁规则

当出现版本冲突时（同一个 artifact 多个版本），Maven 使用**最短路径优先**：

```
A → B → C → log4j 1.2.17     (路径长度 3)
A → D → log4j 1.2.14         (路径长度 2)
→ 选择 log4j 1.2.14（最短路径）
```

如果路径等长：**先声明者优先**。

查看依赖树：

```bash
mvn dependency:tree
```

### 5.5 排除依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>some-lib</artifactId>
    <version>1.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-core</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 5.6 可选依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>optional-dep</artifactId>
    <version>1.0</version>
    <optional>true</optional>
</dependency>
```

`optional=true` 意味着**不传递**——使用此项目的其他项目不会自动拉入此依赖。

### 5.7 快照依赖（SNAPSHOT）

版本号以 `-SNAPSHOT` 结尾表示正在开发中：

```xml
<version>1.0-SNAPSHOT</version>
```

特点：
- Maven 每次构建都会从远程仓库**重新下载** SNAPSHOT 版本（不缓存）
- 适合团队协作中持续集成的场景
- 发布版本（Release）不应使用 SNAPSHOT 依赖

### 5.8 BOM（Bill of Materials）

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.3.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

BOM 可以集中管理一组依赖的版本，子模块声明具体依赖时无需指定版本。

### 5.9 外部依赖（System Scope）

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>custom-lib</artifactId>
    <version>1.0</version>
    <scope>system</scope>
    <systemPath>${project.basedir}/lib/custom-lib.jar</systemPath>
</dependency>
```

> ⚠️ `system` scope 不被推荐——它破坏了可移植性。推荐的做法是将外部 JAR 安装到本地仓库或内部仓库。

---

## 六、仓库系统（Repositories）

### 三级仓库

```
本地仓库（~/.m2/repository）
    ↑ 下载
中央仓库（https://repo.maven.apache.org/maven2）
    ↑ 下载
远程仓库（自定义，如 Nexus、Artifactory）
```

### 配置远程仓库

```xml
<repositories>
    <repository>
        <id>my-repo</id>
        <name>My Internal Repository</name>
        <url>https://nexus.example.com/repository/maven-public/</url>
        <releases>
            <enabled>true</enabled>
            <updatePolicy>daily</updatePolicy>
        </releases>
        <snapshots>
            <enabled>true</enabled>
            <updatePolicy>always</updatePolicy>
        </snapshots>
    </repository>
</repositories>
```

### 修改本地仓库位置

`~/.m2/settings.xml`：

```xml
<settings>
    <localRepository>/data/maven/repository</localRepository>
</settings>
```

### 配置镜像加速（国内必配）

```xml
<!-- settings.xml -->
<mirrors>
    <mirror>
        <id>aliyun-maven</id>
        <mirrorOf>central</mirrorOf>
        <name>阿里云公共仓库</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
</mirrors>
```

---

## 七、构建生命周期、阶段与目标

### 三大内置生命周期

| 生命周期 | 用途 | 关键阶段 |
|---------|------|---------|
| **default** | 项目构建（编译→测试→打包→部署） | validate → compile → test → package → verify → install → deploy |
| **clean** | 清理输出目录 | pre-clean → clean → post-clean |
| **site** | 生成项目文档站点 | pre-site → site → post-site → site-deploy |

### default 生命周期核心阶段

| 阶段 | 说明 |
|------|------|
| `validate` | 验证项目正确性，检查依赖 |
| `initialize` | 初始化构建状态 |
| `generate-sources` | 生成源码（如 ANTLR、JAXB） |
| `process-sources` | 处理源码 |
| `generate-resources` | 生成资源 |
| `process-resources` | 复制资源到输出目录 |
| **`compile`** | 编译源码 |
| `process-classes` | 后处理编译产物 |
| `generate-test-sources` | 生成测试源码 |
| `process-test-sources` | 处理测试源码 |
| `generate-test-resources` | 生成测试资源 |
| `process-test-resources` | 复制测试资源 |
| `test-compile` | 编译测试源码 |
| `process-test-classes` | 后处理测试编译产物 |
| **`test`** | 运行测试 |
| `prepare-package` | 打包前准备 |
| **`package`** | 打包（JAR/WAR/EAR） |
| `pre-integration-test` | 集成测试准备 |
| `integration-test` | 集成测试 |
| `post-integration-test` | 集成测试后处理 |
| `verify` | 验证包是否合格 |
| **`install`** | 安装到本地仓库 |
| **`deploy`** | 部署到远程仓库 |

### 阶段执行语义

```bash
# 执行 package → compile、test、package 都会执行
mvn package

# 多生命周期同时执行
mvn clean install

# 执行某个 goal（插件目标）
mvn dependency:copy-dependencies
mvn help:effective-pom
mvn dependency:tree
```

---

## 八、目录结构

### 标准目录布局

```
my-app/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/          # Java 源码
│   │   ├── resources/     # 资源文件（properties、XML、YAML）
│   │   └── webapp/        # Web 应用（仅 WAR 项目）
│   │       ├── WEB-INF/
│   │       └── index.html
│   └── test/
│       ├── java/          # 测试源码
│       └── resources/     # 测试资源
├── target/                # 构建输出（编译产物、打包结果）
└── README.md
```

### 指定自定义目录

如果无法遵守标准布局，可以在 POM 中覆盖：

```xml
<build>
    <sourceDirectory>${project.basedir}/src</sourceDirectory>
    <testSourceDirectory>${project.basedir}/test</testSourceDirectory>
    <resources>
        <resource>
            <directory>${project.basedir}/config</directory>
        </resource>
    </resources>
</build>
```

---

## 九、构建插件（Plugins）

### 插件与目标的绑定

Maven 的每个功能实际上都由插件提供。Plugin → Goal 的关系：

```
maven-compiler-plugin ──→ compiler:compile （绑定到 compile 阶段）
                       ──→ compiler:testCompile （绑定到 test-compile 阶段）
maven-surefire-plugin  ──→ surefire:test （绑定到 test 阶段）
maven-jar-plugin       ──→ jar:jar （绑定到 package 阶段）
```

### 常用内置插件

| 插件 | 用途 |
|------|------|
| `maven-compiler-plugin` | 编译 Java 源码 |
| `maven-surefire-plugin` | 运行单元测试 |
| `maven-failsafe-plugin` | 运行集成测试 |
| `maven-jar-plugin` | 打包 JAR |
| `maven-war-plugin` | 打包 WAR |
| `maven-source-plugin` | 打包源码 JAR |
| `maven-javadoc-plugin` | 生成 Javadoc |
| `maven-deploy-plugin` | 部署到远程仓库 |
| `maven-install-plugin` | 安装到本地仓库 |
| `maven-shade-plugin` | 打包 Fat JAR（含依赖） |
| `maven-assembly-plugin` | 自定义打包（ZIP/TAR） |
| `maven-release-plugin` | 发布管理 |
| `maven-dependency-plugin` | 依赖分析/复制 |
| `maven-surefire-report-plugin` | 测试报告 |

### 插件配置示例

```xml
<build>
    <plugins>
        <!-- 编译插件 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.13.0</version>
            <configuration>
                <source>21</source>
                <target>21</target>
                <encoding>UTF-8</encoding>
                <compilerArgs>
                    <arg>-Xlint:all</arg>
                </compilerArgs>
            </configuration>
        </plugin>

        <!-- 测试报告 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.2.5</version>
            <configuration>
                <includes>
                    <include>**/*Test.java</include>
                    <include>**/*Tests.java</include>
                </includes>
            </configuration>
        </plugin>

        <!-- Fat JAR -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-shade-plugin</artifactId>
            <version>3.6.0</version>
            <executions>
                <execution>
                    <phase>package</phase>
                    <goals><goal>shade</goal></goals>
                    <configuration>
                        <transformers>
                            <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                <mainClass>com.example.Main</mainClass>
                            </transformer>
                        </transformers>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### Fat JAR 的两种方式

1. **maven-shade-plugin** — 将依赖解压后重新打包（Uber-JAR），可指定 main class，支持资源合并
2. **maven-assembly-plugin** — 更灵活，可生成 ZIP/TAR 等格式，适合含脚本的可分发包

**Spring Boot** 使用自己的 `spring-boot-maven-plugin` 生成可执行 Fat JAR，采用特殊的目录布局（`BOOT-INF/`）。

---

## 十、构建配置（Build Profiles）

### Profile 的应用场景

- 不同环境（开发/测试/生产）使用不同配置
- 按条件启用/禁用某些插件或依赖
- 针对不同 JDK 版本调整构建参数

### 声明 Profile

```xml
<profiles>
    <profile>
        <id>development</id>
        <activation>
            <activeByDefault>true</activeByDefault>
            <jdk>21</jdk>
            <property>
                <name>env</name>
                <value>dev</value>
            </property>
        </activation>
        <properties>
            <db.url>jdbc:h2:mem:dev</db.url>
        </properties>
    </profile>

    <profile>
        <id>production</id>
        <properties>
            <db.url>jdbc:mysql://prod-server:3306/app</db.url>
        </properties>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <configuration>
                        <compilerArgs>
                            <arg>-Xlint:all,-path</arg>
                        </compilerArgs>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

### 激活 Profile

```bash
# 命令行激活
mvn clean package -Pproduction

# settings.xml 中设置默认激活
mvn clean package -Pdevelopment,production

# 通过系统属性激活
mvn clean install -DskipTests=true
```

### Profile 激活条件

| 条件 | 配置方式 |
|------|---------|
| JDK 版本 | `<jdk>17</jdk>` |
| 系统属性 | `<property><name>env</name><value>dev</value></property>` |
| 默认激活 | `<activeByDefault>true</activeByDefault>` |
| 文件存在 | `<file><exists>${basedir}/dev.properties</exists></file>` |
| 文件缺失 | `<file><missing>${basedir}/prod.properties</missing></file>` |

---

## 十一、多模块项目（Multi-Module）

### 聚合 POM

```xml
<!-- parent/pom.xml -->
<groupId>com.example</groupId>
<artifactId>my-project</artifactId>
<version>1.0.0</version>
<packaging>pom</packaging>

<modules>
    <module>common</module>
    <module>api</module>
    <module>web</module>
</modules>
```

### 子模块 POM

```xml
<!-- web/pom.xml -->
<parent>
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0</version>
    <relativePath>../pom.xml</relativePath>
</parent>

<artifactId>web</artifactId>
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>api</artifactId>
    </dependency>
</dependencies>
```

### 目录结构

```
my-project/
├── pom.xml              # 聚合 POM（packaging=pom）
├── common/
│   ├── pom.xml
│   └── src/
├── api/
│   ├── pom.xml
│   └── src/
└── web/
    ├── pom.xml
    └── src/
```

### 优势

- **单一命令构建所有模块**：`mvn clean install` 从根目录执行
- **版本一致性**：所有子模块继承父 POM 中的版本管理
- **增量构建**：Maven 自动确定模块构建顺序（基于依赖图）

---

## 十二、settings.xml 详解

### 作用域

| 文件位置 | 作用范围 |
|---------|---------|
| `$M2_HOME/conf/settings.xml` | 全局（该 Maven 安装的所有用户） |
| `~/.m2/settings.xml` | 当前用户（若存在则覆盖全局同名配置） |

### 常用配置

```xml
<settings>
    <!-- 1. 本地仓库位置 -->
    <localRepository>/data/maven/repository</localRepository>
    
    <!-- 2. 代理服务器 -->
    <proxies>
        <proxy>
            <id>internal-proxy</id>
            <active>true</active>
            <protocol>http</protocol>
            <host>proxy.example.com</host>
            <port>8080</port>
            <nonProxyHosts>*.local|*.internal</nonProxyHosts>
        </proxy>
    </proxies>
    
    <!-- 3. 服务器认证信息 -->
    <servers>
        <server>
            <id>my-private-repo</id>
            <username>deploy-user</username>
            <password>encrypted-password</password>
        </server>
    </servers>
    
    <!-- 4. 镜像（覆盖中央仓库） -->
    <mirrors>
        <mirror>
            <id>aliyun</id>
            <mirrorOf>central</mirrorOf>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>
    
    <!-- 5. 全局 Profile（所有项目共享） -->
    <profiles>
        <profile>
            <id>java21</id>
            <activation>
                <jdk>21</jdk>
            </activation>
            <properties>
                <maven.compiler.source>21</maven.compiler.source>
                <maven.compiler.target>21</maven.compiler.target>
            </properties>
        </profile>
    </profiles>
    
    <!-- 6. 默认激活的 Profile -->
    <activeProfiles>
        <activeProfile>java21</activeProfile>
    </activeProfiles>
</settings>
```

---

## 十三、Maven vs Ant vs Gradle

| 维度 | Maven | Ant | Gradle |
|------|-------|-----|--------|
| **范式** | 声明式（what） | 命令式（how） | 声明式 + 编程式 |
| **配置文件** | XML（pom.xml） | XML（build.xml） | Groovy/Kotlin DSL |
| **约定** | 强约定 | 无约定 | 有约定但可自定义 |
| **依赖管理** | 内置（传递依赖） | 无（需自己 Ivy） | 内置（更灵活） |
| **构建速度** | 中等 | 快（无生命周期） | 快（增量编译 + 缓存） |
| **学习曲线** | 中 | 低 | 高（DSL 灵活度高） |
| **多模块** | 优秀（继承+聚合） | 手动 | 优秀 |
| **插件生态** | 成熟 | 较少 | 活跃 |
| **典型使用场景** | 企业级 Java 项目 | 遗留项目 | Android、高性能项目 |

### 何时选择 Maven

- 标准 Java 企业项目（Spring Boot 官方推荐）
- 团队需要一致的构建规范
- 项目依赖管理复杂（大量传递依赖）
- 需要与 CI/CD 深度集成（Jenkins、GitLab CI）

### 何时选择 Gradle

- 需要灵活的构建逻辑（多语言、复杂的构建条件）
- Android 开发（Gradle 是官方标准）
- 构建速度敏感（增量编译、构建缓存）
- 希望使用更简洁的 DSL 而非 XML

---

## 十四、常用命令速查

```bash
# 构建与生命周期
mvn compile                        # 编译源码
mvn test                           # 运行测试
mvn package                        # 打包（不部署）
mvn install                        # 打包 + 安装到本地仓库
mvn deploy                         # 打包 + 部署到远程仓库
mvn clean                          # 清理 target/
mvn clean install                  # 清理 + 完整构建（最常用）

# 多生命周期
mvn clean verify                   # 清理 + 构建到 verify 阶段（含集成测试检查）

# 跳过步骤
mvn package -DskipTests            # 跳过测试编译和执行
mvn package -Dmaven.test.skip=true # 完全跳过测试（连测试编译都跳过）
mvn install -Dcheckstyle.skip=true # 跳过代码检查

# 调试与诊断
mvn -v                             # 版本信息
mvn -X                             # 调试模式（打印详细日志）
mvn help:effective-pom             # 查看有效 POM
mvn dependency:tree                # 查看依赖树（诊断版本冲突）
mvn dependency:analyze             # 分析未使用/未声明的依赖
mvn dependency:copy-dependencies   # 复制所有依赖到 target/dependency/
mvn help:describe -Dplugin=compiler # 查看插件详情

# Profiles
mvn package -Pproduction           # 使用 production profile
mvn package -Pdev,test             # 同时激活多个 profile

# 离线构建
mvn package -o                     # 离线模式（不从远程拉取）

# 多线程构建（Maven 3+）
mvn -T 4 package                   # 使用 4 个线程并行构建
mvn -T 1C package                  # 每个 CPU 核心一个线程

# 构建特定模块及依赖
mvn install -pl web                # 只构建 web 模块
mvn install -pl web -am            # 构建 web 模块及其依赖模块
mvn install -rf web                # 从 web 模块开始继续构建
```

---

## 十五、最佳实践与常见坑

### 最佳实践

1. **版本统一管理**：在 `<properties>` 中定义所有版本号，或使用 BOM（Bill of Materials）

2. **dependencyManagement 先行**：在父 POM 中用 `dependencyManagement` 锁定版本，子模块只需声明 `groupId` + `artifactId`

3. **不要提交 target/ 目录**：在 `.gitignore` 中添加 `/target/`、`*.class`、`*.jar`

4. **指定编码**：始终设置 `project.build.sourceEncoding=UTF-8`，避免跨平台乱码

5. **使用 `.mvn` 目录**：项目根目录创建 `.mvn/jvm.config` 可配置 JVM 参数，`maven.config` 可配置默认 Maven 参数

6. **构建黄金命令**：CI/CD 中使用 `mvn clean verify`（验证阶段会检查代码规范和集成测试）

7. **管理传递依赖**：定期运行 `mvn dependency:tree` 了解依赖关系，用 `exclusions` 排除冲突版本

8. **使用 `.mvn/maven.config`**：
   ```
   # .mvn/maven.config
   -T 4
   --no-transfer-progress
   -Dmaven.test.failure.ignore=true
   ```

### 常见坑

| 问题 | 原因 | 解决 |
|------|------|------|
| **jar 包下载失败** | 网络问题或中央仓库被墙 | 配置阿里云镜像 |
| **版本冲突** | 传递依赖引入多个版本 | `mvn dependency:tree` 分析，用 `exclusions` |
| **找不到符号** | JDK 版本不匹配 | 检查 `maven-compiler-plugin` 的 source/target |
| **surefire 不运行测试** | 测试类命名不符合 `*Test.java` | 使用 `*Test.java` 或 `*Tests.java` 命名 |
| **多模块构建顺序错误** | 模块间依赖声明不全 | 确保子模块正确声明 inter-module 依赖 |
| **resources 未被复制** | 默认只复制 `src/main/resources` | 在 `<build><resources>` 中显式添加 |
| **${user.home} 变量问题** | 某些平台解析不一致 | 避免在 pom.xml 中直接使用，用 settings.xml |
| **deploy 401/403** | 仓库认证信息未配置 | 在 settings.xml 中添加 `<servers>` 配置 |

---

## 十六、Maven 4.x 新特性（简述）

Maven 4（2024 年发布）带来了以下重要变化：

- **CI-friendly 属性文件**：支持 `pom.properties` 在构建时注入版本号而不修改 `pom.xml`
- **改进的消息系统**：更清晰的构建失败提示和解决方案建议
- **POM 类型检查**：在 validate 阶段验证 POM 的语义正确性
- **模块并行构建优化**：更好的 `-T` 多线程调度
- **Maven Resolver**：替代旧的 Aether，依赖解析性能提升
- **改进的插件管理**：支持插件版本范围

---

## 十七、资源与参考

- **官方文档**: [https://maven.apache.org/guides/](https://maven.apache.org/guides/)
- **POM 参考**: [https://maven.apache.org/pom.html](https://maven.apache.org/pom.html)
- **Settings 参考**: [https://maven.apache.org/settings.html](https://maven.apache.org/settings.html)
- **生命周期参考**: [https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)
- **插件列表**: [https://maven.apache.org/plugins/](https://maven.apache.org/plugins/)
- **阿里云镜像**: [https://developer.aliyun.com/mvn/guide](https://developer.aliyun.com/mvn/guide)
- **Maven Central**: [https://search.maven.org/](https://search.maven.org/)
- **Maven Repository Search**: [https://mvnrepository.com/](https://mvnrepository.com/)

---

> **整理说明：** 本文基于 Jakob Jenkov 的 Maven Tutorial 进行翻译、重组和大幅扩充。原文侧重于 Maven 3.6 的核心概念，本文在此基础上增加了 scopes 表格、依赖仲裁规则、BOM、多模块项目管理、settings.xml 完整配置、Maven vs Ant vs Gradle 对比、常用命令速查、最佳实践与常见坑、Maven 4.x 新特性等深度内容。

> *Processed on 2026-06-21 from https://jenkov.com/tutorials/maven/maven-tutorial.html*
