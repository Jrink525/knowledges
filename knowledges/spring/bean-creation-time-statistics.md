---
title: Spring Boot 性能优化 — 统计 Bean 创建耗时
tags: [spring, spring-boot, performance, bean-lifecycle, optimization, ApplicationContextFactory, 来源:公众号]
category: spring/performance
source: https://mp.weixin.qq.com/s/TcdqQ27ZScGUtfMmuXw6uQ
date: 2026-05-21
---

# 性能优化 — Spring Boot 统计 Bean 创建耗时

> **环境：** Spring Boot 3.5.0
> **来源：** Spring Boot 3实战案例锦集

---

## 背景

Spring Boot 项目启动优化中，Bean 创建耗时可能是关键瓶颈。传统监控手段难以精准统计单个 Bean 的实例化和初始化全耗时，尤其无法区分 **依赖 Bean 耗时** 与 **自身耗时**。

本文通过自定义 `ApplicationContextFactory` → `Environment` → `BeanFactory`，**底层拦截 Bean 创建流程**，实现无侵入、高精度的耗时统计。

---

## 架构设计

```
SpringApplication.run()
    ↓
ApplicationContextFactory.create()     ← 自定义工厂
    ↓
ConfigurableEnvironment.create()       ← 自定义环境
    ↓
DefaultListableBeanFactory             ← 自定义 BeanFactory（重写 createBean）
    ↓
createBean() 拦截 → 记录 start/end → 输出耗时
```

---

## 1. 自定义 ApplicationContextFactory

```java
@Order(Ordered.HIGHEST_PRECEDENCE)
public class PackServletWebServerApplicationContextFactory
        implements ApplicationContextFactory {

    @Override
    public Class<? extends ConfigurableEnvironment> getEnvironmentType(
            WebApplicationType webApplicationType) {
        return webApplicationType != WebApplicationType.SERVLET
                ? null : PackApplicationServletEnvironment.class;
    }

    @Override
    public ConfigurableEnvironment createEnvironment(WebApplicationType webApplicationType) {
        return webApplicationType != WebApplicationType.SERVLET
                ? null : new PackApplicationServletEnvironment();
    }

    @Override
    public ConfigurableApplicationContext create(WebApplicationType webApplicationType) {
        return webApplicationType != WebApplicationType.SERVLET
                ? null : createContext();
    }

    private ConfigurableApplicationContext createContext() {
        PackListableBeanFactory beanFactory = new PackListableBeanFactory();
        if (!AotDetector.useGeneratedArtifacts()) {
            AnnotationConfigServletWebServerApplicationContext context =
                    new AnnotationConfigServletWebServerApplicationContext(beanFactory);
            beanFactory.setContext(context);
            return context;
        }
        ServletWebServerApplicationContext context =
                new ServletWebServerApplicationContext(beanFactory);
        beanFactory.setContext(context);
        return context;
    }
}
```

### 注册

在 `META-INF/spring.factories` 中配置：

```properties
org.springframework.boot.ApplicationContextFactory=\
com.pack.PackServletWebServerApplicationContextFactory
```

> Spring Boot 3.4+ 推荐使用 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，但 `ApplicationContextFactory` 的 SPI 仍通过 `spring.factories` 注册。

---

## 2. 自定义 Environment

```java
public class PackApplicationServletEnvironment extends StandardServletEnvironment {

    @Override
    protected String doGetActiveProfilesProperty() {
        return null;
    }

    @Override
    protected String doGetDefaultProfilesProperty() {
        return null;
    }

    @Override
    protected ConfigurablePropertyResolver createPropertyResolver(
            MutablePropertySources propertySources) {
        return ConfigurationPropertySources.createPropertyResolver(propertySources);
    }
}
```

> 这里禁用了默认的 profiles 逻辑，并切换为 Spring Boot 的 `ConfigurationPropertySources` 解析器，以支持 `@ConfigurationProperties` 绑定。

---

## 3. 自定义 BeanFactory（核心）

```java
public class PackListableBeanFactory extends DefaultListableBeanFactory {

    // Bean 创建耗时统计：beanName → 纳秒
    private static final Map<String, Long> beanCreationTimeNanos = new ConcurrentHashMap<>();
    // 汇总数据：beanName → 毫秒
    private static final Map<String, Double> beanCreationTimeMillis = new ConcurrentHashMap<>();

    private ApplicationContext context;
    private volatile boolean initialized = false;
    private final List<String> excludePackages = new ArrayList<>();

    @Override
    protected Object createBean(String beanName, RootBeanDefinition mbd, Object[] args)
            throws BeanCreationException {

        // 首次执行时读取排除配置
        if (!initialized) {
            Binder.get(this.context.getEnvironment())
                    .bind("pack.statistics.exclude", Bindable.ofInstance(excludePackages));
            initialized = true;
        }

        // 排除指定包下的 Bean（如框架自身的 Bean）
        Class<?> beanClass = resolveBeanClass(mbd, beanName);
        if (beanClass == null) {
            beanClass = mbd.getTargetType();
        }
        if (beanClass != null && isExcluded(beanClass)) {
            return super.createBean(beanName, mbd, args);
        }

        long start = System.nanoTime();
        Object bean = super.createBean(beanName, mbd, args);
        long end = System.nanoTime();

        long durationNanos = end - start;
        double durationMillis = durationNanos / 1_000_000.0;

        beanCreationTimeNanos.put(beanName, durationNanos);
        beanCreationTimeMillis.put(beanName, durationMillis);

        // 慢 Bean 警告（> 500ms）
        if (durationMillis > 500) {
            System.err.printf("🐢 [慢Bean] %s 创建耗时: %.2f ms%n", beanName, durationMillis);
        }

        return bean;
    }

    private boolean isExcluded(Class<?> beanClass) {
        String pkg = beanClass.getPackageName();
        return excludePackages.stream().anyMatch(p -> pkg.startsWith(p));
    }

    public void setContext(ApplicationContext context) {
        this.context = context;
    }

    // ====== 静态统计方法 ======

    public static Map<String, Double> getBeanCreationTimes() {
        return Collections.unmodifiableMap(beanCreationTimeMillis);
    }

    public static double getTotalCreationTimeMs() {
        return beanCreationTimeMillis.values().stream().mapToDouble(Double::doubleValue).sum();
    }

    public static List<String> getSlowBeans(double thresholdMs) {
        return beanCreationTimeMillis.entrySet().stream()
                .filter(e -> e.getValue() > thresholdMs)
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .map(e -> String.format("%s: %.2f ms", e.getKey(), e.getValue()))
                .toList();
    }

    public static void printStatistics() {
        System.out.println("\n====== Bean 创建耗时统计 ======");
        beanCreationTimeMillis.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .forEach(e -> System.out.printf("  %-50s %.2f ms%n", e.getKey(), e.getValue()));
        System.out.printf("  %-50s %.2f ms%n", "[合计]", getTotalCreationTimeMs());
        System.out.println("===============================\n");
    }
}
```

### 配置文件排除包

```yaml
pack:
  statistics:
    exclude:
      - org.springframework
      - org.apache
      - com.zaxxer
```

---

## 4. 测试

### 模拟耗时 Bean

```java
@Configuration
public class CustomConfig {

    @Bean
    Date slowDateBean() {
        try { TimeUnit.SECONDS.sleep(2); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return new Date();
    }
}

@Component
public class SlowBeanB {

    @Resource
    private Date slowDateBean;

    @PostConstruct
    public void init() {
        try { TimeUnit.SECONDS.sleep(3); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
```

### 控制台输出

启动后调用 `PackListableBeanFactory.printStatistics()` 查看输出：

```
====== Bean 创建耗时统计 ======
  slowBeanB                                          3502.15 ms
  customConfig.slowDateBean                          2001.33 ms
  userService                                         102.45 ms
  orderRepository                                      45.67 ms
  [合计]                                             5651.60 ms
===============================
```

> **注意：** `slowBeanB` 的耗时包含了它依赖的 `slowDateBean` 耗时。如果需要排除依赖耗时，需进一步重写 `getDependentBeans()` 逻辑。

---

## 5. 🚀 增强方案：Actuator 端点暴露

创建 Actuator 端点查看运行时 Bean 耗时统计：

```java
@Component
@Endpoint(id = "bean-timing")
public class BeanTimingEndpoint {

    @ReadOperation
    public Map<String, Object> beanTiming() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("totalTimeMs", PackListableBeanFactory.getTotalCreationTimeMs());
        result.put("beanCount", PackListableBeanFactory.getBeanCreationTimes().size());
        result.put("slowBeans (>500ms)", PackListableBeanFactory.getSlowBeans(500));
        result.put("allBeans", PackListableBeanFactory.getBeanCreationTimes());
        return result;
    }
}
```

访问 `GET /actuator/bean-timing` 即可查看。

## 6. 🚀 增强方案：Spring Boot 2.x/3.x 通用监听器方式

如果不想自定义 BeanFactory（侵入性较大），可使用 Spring ApplicationListener 监听 `ApplicationReadyEvent`，结合 `ApplicationContext.getBeanFactory()` 反射获取统计，或直接用 AOP 实现：

```java
@Component
public class StartupTimeListener implements ApplicationListener<ApplicationReadyEvent> {

    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        ConfigurableApplicationContext context = event.getApplicationContext();
        // 获取 refresh 耗时
        long startupTime = event.getTimeTaken().toMillis();
        System.out.printf("应用启动完成，总耗时: %d ms%n", startupTime);

        // 如果使用了 PackListableBeanFactory
        DefaultListableBeanFactory bf = (DefaultListableBeanFactory) context.getBeanFactory();
        if (bf instanceof PackListableBeanFactory) {
            PackListableBeanFactory.printStatistics();
        }
    }
}
```

---

## 总结

| 方案 | 侵入性 | 精度 | 适用场景 |
|------|--------|------|---------|
| 自定义 BeanFactory | 高 | 精确到每个 Bean | 性能调优、慢 Bean 排查 |
| ApplicationReadyEvent | 低 | 仅总耗时 | 简单的启动耗时监控 |
| AOP + @PostConstruct | 中 | 仅初始化方法 | 不需要 Bean 实例化耗时 |
| Micrometer / Actuator | 低 | 运行时指标 | 生产环境持续监控 |

---

*本文整理自公众号「Springboot实战案例锦集」，代码经增强和补充注释。*
