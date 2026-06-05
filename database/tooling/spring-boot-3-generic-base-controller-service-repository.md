---
title: "Spring Boot 3 通用 BaseController / BaseService / BaseRepository 实战"
source: "https://mp.weixin.qq.com/s/e3i2v7IhFsDjrraDdC5e-A"
author: "公众号 Spring Boot 实战案例合集"
date: 2026-05-28
tags:
  - spring-boot
  - spring-boot-3
  - jpa
  - base-controller
  - base-service
  - base-repository
  - generic-crud
  - mapstruct-plus
  - specification
  - dynamic-query
  - pagination
category: "ai-tools/spring-ai"
complementary:
  - "Spring Data JPA Specifications (docs.spring.io)"
  - "Spring Data JPA Custom Implementations (docs.spring.io)"
---

# Spring Boot 3 通用 BaseController / BaseService / BaseRepository 实战

> **来源：** Spring Boot 实战案例合集（付费文章）  
> **补充参考：** [Spring Data JPA Specifications](https://docs.spring.io/spring-data/jpa/reference/jpa/specifications.html) · [Custom Repository Implementations](https://docs.spring.io/spring-data/jpa/reference/repositories/custom-implementations.html)
> **环境：** Spring Boot 3.5.0 · JDK 17+ · Spring Data JPA · MapStruct-Plus

---

## 一、引言

在软件开发生命周期中，随着项目规模不断扩大和业务复杂度持续提升，代码复用与标准化成为关键诉求。

传统的四层架构（Controller → Service → DAO/Repository）在编写多个业务域时，存在大量重复的 CRUD 代码，不仅降低了开发效率，还增加了维护成本。每个新的业务实体都需要重新编写：

- Repository 接口（基本的 `findById`、`save`、`delete` 等方法声明）
- Service 类（CRUD 逻辑、参数校验、异常处理、DTO 转换）
- Controller 类（REST 端点、请求/响应封装、分页查询）

为了解决这一问题，实现**通用的 BaseController、BaseService、BaseRepository** 组件是非常有必要的。它能：

1. **统一规范** — 所有业务域遵循相同的 CRUD 接口和异常处理模式
2. **提升可维护性** — 核心逻辑集中管理，修改一处全盘生效
3. **让开发人员更聚焦业务逻辑** — 仅需声明对应的类，便能自动获得完整的 CRUD 和动态查询能力

**最终效果：**

```java
// ===== DAO & Repository =====
public interface MedicineRepository extends BaseRepository<Medicine, String> {
}

// ===== Service =====
@Service
public class MedicineService extends BaseService<Medicine, String> {
}

// ===== Controller =====
@RestController
@RequestMapping("/medicines")
public class MedicineController extends BaseController<Medicine, MedicineDTO, String> {
}
```

仅需以上声明，无需编写任何方法实现，即可获得完整的 RESTful CRUD 和动态查询能力。

---

## 二、项目依赖与环境

### 2.1 Maven 依赖

```xml
<!-- Spring Boot Starter Data JPA -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<!-- Spring Boot Starter Web -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- MapStruct-Plus：实体 ↔ DTO 高性能转换（基于 getter/setter，无反射） -->
<dependency>
    <groupId>io.github.linpeilie</groupId>
    <artifactId>mapstruct-plus-spring-boot-starter</artifactId>
</dependency>

<!-- Spring Boot Starter Validation -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

### 2.2 核心依赖说明

| 依赖 | 作用 |
|------|------|
| `spring-boot-starter-data-jpa` | JPA + Hibernate + 自动 Repository 实现 |
| `io.github.linpeilie:mapstruct-plus` | 编译期生成 getter/setter 转换代码，零反射高性能 DTO 映射 |
| `spring-boot-starter-validation` | Jakarta Bean Validation（`@Valid`、`@NotBlank` 等） |

### 2.3 application.yml 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf-8
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
```

---

## 三、BaseRepository — 通用数据访问层

### 3.1 基础接口

最基础的实现是直接继承 Spring Data JPA 提供的复合接口。`JpaRepository` 已提供 `save`、`findById`、`findAll`、`delete` 等基本方法，`JpaSpecificationExecutor` 提供动态查询支持。

```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.NoRepositoryBean;

/**
 * 通用 Repository 接口
 * @param <T>  实体类型
 * @param <ID> 主键类型
 */
@NoRepositoryBean
public interface BaseRepository<T, ID> extends JpaRepository<T, ID>, JpaSpecificationExecutor<T> {
}
```

> **`@NoRepositoryBean`** 注解告诉 Spring Data 不要为这个接口创建代理实例——它只是多个实际 Repository 的父接口。

### 3.2 可扩展的自定义 Repository 实现

当需要实现标准 CRUD 之外的底层操作（如悲观锁、批量更新、自定义查询）时，推荐使用 Spring Data 的 **Fragment 组合模式**（Spring Data 官方推荐的方式，取代了早期单一 `Impl` 后缀约定）。

**第一步：定义 Fragment 接口**

```java
import jakarta.persistence.LockModeType;

/**
 * 可扩展 Repository 接口
 */
public interface ExtensibleRepository<T, ID> {

    /**
     * 带锁模式的查询
     * @param entityClass 实体类
     * @param id          主键
     * @param lockMode    锁模式（如 PESSIMISTIC_WRITE）
     * @return 实体对象
     */
    T lockById(Class<T> entityClass, ID id, LockModeType lockMode);

    /**
     * 批量刷新（适用于批量操作后统一刷新持久化上下文）
     */
    void flush();
}
```

**第二步：实现 Fragment**

```java
import jakarta.persistence.EntityManager;
import jakarta.persistence.LockModeType;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;

public class ExtensibleRepositoryImpl<T, ID> implements ExtensibleRepository<T, ID> {

    @PersistenceContext
    private EntityManager entityManager;

    @Override
    @Transactional
    public T lockById(Class<T> entityClass, ID id, LockModeType lockMode) {
        return this.entityManager.find(entityClass, id, lockMode);
    }

    @Override
    public void flush() {
        this.entityManager.flush();
    }
}
```

> 核心是 `@PersistenceContext EntityManager` — 它是 JPA 底层的核心 API，提供了远超 Spring Data 自动方法的灵活度。

**第三步：组合到 Repository**

```java
// 最终 Repository 继承 BaseRepository（含基本 CRUD + 动态查询）和 ExtensibleRepository（自定义功能）
public interface MedicineRepository extends BaseRepository<Medicine, String>, ExtensibleRepository<Medicine, String> {
    // 还可添加自定义查询方法
}
```

这是 Spring Data 官方文档中描述的 **fragment 编程模型**（[Custom Implementations](https://docs.spring.io/spring-data/jpa/reference/repositories/custom-implementations.html)）：
> "Repositories may be composed of multiple custom implementations that are imported in the order of their declaration. Custom implementations have a higher priority than the base implementation."

---

## 四、BaseComponent — 公共组件基类

Service 层的公共基类，提供国际化消息支持等基础能力。

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.MessageSource;
import org.springframework.context.i18n.LocaleContextHolder;

/**
 * 公共组件基类
 */
public abstract class BaseComponent {

    @Autowired
    private MessageSource messageSource;

    /**
     * 获取国际化消息
     * @param code 消息编码
     * @return 本地化消息字符串
     */
    protected String getMessage(String code) {
        return messageSource.getMessage(code, null, LocaleContextHolder.getLocale());
    }

    /**
     * 获取带参数的国际化消息
     * @param code  消息编码
     * @param args  参数
     * @return 本地化消息字符串
     */
    protected String getMessage(String code, Object[] args) {
        return messageSource.getMessage(code, args, LocaleContextHolder.getLocale());
    }
}
```

对应的 `messages.properties`：

```properties
# messages.properties
common.baseservice.entity.notfound=实体对象不存在, id: {0}
common.baseservice.id.isnull=主键ID不能为空
common.baseservice.class.error=转换目标类型不能为空
common.baseservice.entity.isnull=实体对象不能为空
common.baseservice.page.invalid=分页参数无效
```

---

## 五、BaseService — 通用业务逻辑层

这是整个通用架构的核心。BaseService 封装了所有常见的 CRUD 操作和动态分页查询。

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import jakarta.persistence.EntityNotFoundException;

import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * 通用业务服务基类
 * @param <T>  实体类型
 * @param <ID> 主键类型
 */
public abstract class BaseService<T, ID> extends BaseComponent {

    private static final String COMMON_BASESERVICE_ENTITY_NOTFOUND = "common.baseservice.entity.notfound";
    private static final String COMMON_BASESERVICE_ID_ISNULL      = "common.baseservice.id.isnull";
    private static final String COMMON_BASESERVICE_CLASS_ERROR    = "common.baseservice.class.error";
    private static final String COMMON_BASESERVICE_ENTITY_ISNULL  = "common.baseservice.entity.isnull";

    protected BaseRepository<T, ID> repository;
    protected Converter           converter;

    // ======================== 增 ========================

    /**
     * 保存单个实体
     */
    @Transactional
    public T save(T entity) {
        if (Objects.isNull(entity)) {
            throw new CommonException(getMessage(COMMON_BASESERVICE_ENTITY_ISNULL));
        }
        return this.repository.saveAndFlush(entity);
    }

    /**
     * 批量保存实体
     */
    @Transactional
    public List<T> save(List<T> entities) {
        if (entities == null || entities.isEmpty()) {
            return Collections.emptyList();
        }
        return this.repository.saveAllAndFlush(entities);
    }

    // ======================== 删 ========================

    /**
     * 根据 ID 删除
     */
    @Transactional
    public void deleteById(ID id) {
        validateId(id);
        this.repository.deleteById(id);
    }

    /**
     * 根据 ID 集合批量删除
     */
    @Transactional
    public void deleteAllById(List<ID> ids) {
        if (ids == null || ids.isEmpty()) {
            return;
        }
        List<ID> finalIds = ids.stream()
                               .filter(Objects::nonNull)
                               .collect(Collectors.toList());
        this.repository.deleteAllById(finalIds);
    }

    /**
     * 删除实体对象
     */
    @Transactional
    public void delete(T entity) {
        if (Objects.isNull(entity)) {
            throw new CommonException(getMessage(COMMON_BASESERVICE_ENTITY_ISNULL));
        }
        this.repository.delete(entity);
    }

    // ======================== 查（单个）=====================

    /**
     * 根据 ID 查询（返回 Optional）
     */
    public Optional<T> queryById(ID id) {
        validateId(id);
        return this.repository.findById(id);
    }

    /**
     * 根据 ID 查询，不存在则抛出 EntityNotFoundException
     */
    public T getEntity(ID id) {
        validateId(id);
        return this.repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException(
                        getMessage(COMMON_BASESERVICE_ENTITY_NOTFOUND, new Object[]{id})));
    }

    // ======================== 查（批量）=====================

    /**
     * 根据 ID 集合批量查询
     */
    public List<T> findAllById(List<ID> ids) {
        return this.repository.findAllById(ids);
    }

    // ======================== 存在性 & 计数 =================

    /**
     * 检查实体是否存在
     */
    public boolean existsById(ID id) {
        validateId(id);
        return this.repository.existsById(id);
    }

    /**
     * 数据总数
     */
    public long count() {
        return this.repository.count();
    }

    /**
     * 根据条件统计总数
     */
    public long count(Specification<T> specification) {
        return this.repository.count(specification);
    }

    // ======================== 分页查询 ======================

    /**
     * 基于 Specification 分页查询并转换为 DTO
     * @param specification JPA 查询条件
     * @param pageQuery     分页参数
     * @param clazz         DTO 类型
     */
    public <S> Pager<S> queryPager(Specification<T> specification, PageQuery pageQuery, Class<S> clazz) {
        if (clazz == null || clazz == void.class) {
            throw new CommonException(getMessage(COMMON_BASESERVICE_CLASS_ERROR));
        }
        Pager<T> pager = Pager.query(specification, pageQuery, repository);
        List<S> result = this.converter.convert((List<T>) pager.getRows(), clazz);
        return new Pager<>(pager.getPageNum(), pager.getTotal(), pager.getPageSize(), pager.getTotalPage(), result);
    }

    /**
     * 无条件分页查询（全量数据分页）
     */
    public <S> Pager<S> queryPager(PageQuery pageQuery, Class<S> clazz) {
        Specification<T> specification = (root, query, criteriaBuilder) -> query.getRestriction();
        return this.queryPager(specification, pageQuery, clazz);
    }

    /**
     * 基于 DTO 条件的动态分页查询
     * @param condition 查询条件 DTO（继承 BaseDTO）
     * @param pageQuery 分页参数
     * @param clazz     返回的 DTO 类型
     */
    public <S, P extends BaseDTO> Pager<S> queryPagerByCondition(P condition, PageQuery pageQuery, Class<S> clazz) {
        Specification<T> specification = new BaseSpecification<>(condition);
        return this.queryPager(specification, pageQuery, clazz);
    }

    // ======================== 内部工具方法 ==================

    private void validateId(ID id) {
        if (id == null) {
            throw new CommonException(getMessage(COMMON_BASESERVICE_ID_ISNULL));
        }
    }

    @Autowired
    public void setRepository(BaseRepository<T, ID> repository) {
        this.repository = repository;
    }

    @Autowired
    public void setConverter(Converter converter) {
        this.converter = converter;
    }
}
```

### 方法汇总

| 方法 | 说明 |
|------|------|
| `save(T)` / `save(List<T>)` | 单个/批量保存（含 flush） |
| `deleteById(ID)` / `deleteAllById(List<ID>)` / `delete(T)` | 按 ID 或按实体删除 |
| `queryById(ID)` | 返回 `Optional<T>` |
| `getEntity(ID)` | 不存在时抛 `EntityNotFoundException` |
| `findAllById(List<ID>)` | 批量查找 |
| `existsById(ID)` / `count()` | 存在性检查 / 总数统计 |
| `count(Specification)` | 条件统计 |
| `queryPager(spec, pageQuery, dtoClass)` | Specification 分页 + DTO 转换 |
| `queryPager(pageQuery, dtoClass)` | 无条件全量分页 |
| `queryPagerByCondition(dto, pageQuery, dtoClass)` | DTO 条件驱动的动态分页 |

---

## 六、BaseController — 通用控制层

BaseController 提供了标准的 RESTful 端点模板，子类只需声明继承关系即可获得完整的 API。

```java
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 通用 Controller 基类
 * @param <T>      实体类型
 * @param <D>      DTO 类型（接收/返回的数据对象）
 * @param <ID>     主键类型
 */
public abstract class BaseController<T, D, ID> {

    @Autowired
    protected BaseService<T, ID> baseService;

    @Autowired
    protected Converter converter;

    /**
     * 获取实体对应的 DTO 类型（子类可重写）
     */
    protected abstract Class<D> getDtoClass();

    // ======================== POST ========================

    /**
     * 新增实体
     * POST /api/{entity}
     */
    @PostMapping
    public Result<D> create(@Valid @RequestBody D dto) {
        T entity = converter.convert(dto, getEntityClass());
        T saved = baseService.save(entity);
        return Result.success(converter.convert(saved, getDtoClass()));
    }

    /**
     * 批量新增
     * POST /api/{entity}/batch
     */
    @PostMapping("/batch")
    public Result<List<D>> createBatch(@Valid @RequestBody List<D> dtos) {
        List<T> entities = converter.convert(dtos, getEntityClass());
        List<T> saved = baseService.save(entities);
        return Result.success(converter.convert(saved, getDtoClass()));
    }

    // ======================== DELETE =======================

    /**
     * 根据 ID 删除
     * DELETE /api/{entity}/{id}
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable ID id) {
        baseService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     * DELETE /api/{entity}/batch
     */
    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody List<ID> ids) {
        baseService.deleteAllById(ids);
        return Result.success();
    }

    // ======================== PUT ========================

    /**
     * 更新实体
     * PUT /api/{entity}/{id}
     *
     * 注：此为基础实现，复杂业务可重写。建议在 Service 层实现 update 方法，
     *     使用 EntityManager.merge() 或先查询再更新字段。
     */
    @PutMapping("/{id}")
    public Result<D> update(@PathVariable ID id, @Valid @RequestBody D dto) {
        // 先检查是否存在
        T existing = baseService.getEntity(id);
        // 将 DTO 字段合并到已存在的实体中
        converter.update(dto, existing);
        T saved = baseService.save(existing);
        return Result.success(converter.convert(saved, getDtoClass()));
    }

    // ======================== GET ========================

    /**
     * 根据 ID 查询
     * GET /api/{entity}/{id}
     */
    @GetMapping("/{id}")
    public Result<D> getById(@PathVariable ID id) {
        T entity = baseService.getEntity(id);
        return Result.success(converter.convert(entity, getDtoClass()));
    }

    // ======================== 分页查询 ========================

    /**
     * 分页查询
     * GET /api/{entity}/page?pageNum=1&pageSize=10&sortBy=createTime&sortDir=desc
     */
    @GetMapping("/page")
    public Result<Pager<D>> page(PageQuery pageQuery) {
        Pager<D> pager = baseService.queryPager(pageQuery, getDtoClass());
        return Result.success(pager);
    }

    /**
     * 带条件的动态分页查询
     * POST /api/{entity}/page/condition
     * Body: { "name": "xxx", "status": 1, ... }
     */
    @PostMapping("/page/condition")
    public Result<Pager<D>> pageByCondition(@RequestBody BaseDTO condition, PageQuery pageQuery) {
        Pager<D> pager = baseService.queryPagerByCondition(condition, pageQuery, getDtoClass());
        return Result.success(pager);
    }

    // ======================== 获取实体 Class =================

    /**
     * 获取泛型 T 的实际 Class（通过反射）
     * 子类可重写以提供精确的 Class 类型
     */
    @SuppressWarnings("unchecked")
    protected Class<T> getEntityClass() {
        java.lang.reflect.Type superClass = getClass().getGenericSuperclass();
        if (superClass instanceof java.lang.reflect.ParameterizedType) {
            return (Class<T>) ((java.lang.reflect.ParameterizedType) superClass)
                    .getActualTypeArguments()[0];
        }
        throw new IllegalStateException("Unable to resolve entity class from generic parameter");
    }
}
```

### BaseController 自动提供的端点

| HTTP | 端点 | 方法 | 说明 |
|------|------|------|------|
| `POST` | `/{entity}` | `create` | 新增 |
| `POST` | `/{entity}/batch` | `createBatch` | 批量新增 |
| `DELETE` | `/{entity}/{id}` | `delete` | 按 ID 删除 |
| `DELETE` | `/{entity}/batch` | `deleteBatch` | 批量删除 |
| `PUT` | `/{entity}/{id}` | `update` | 更新（先查再合并） |
| `GET` | `/{entity}/{id}` | `getById` | 按 ID 查询 |
| `GET` | `/{entity}/page` | `page` | 无条件分页 |
| `POST` | `/{entity}/page/condition` | `pageByCondition` | 动态条件分页 |

---

## 七、BaseSpecification — 动态查询引擎

核心能力：根据 DTO 中的非空字段自动构建 JPA `Specification`，实现即时的动态查询。

```java
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import org.springframework.data.jpa.domain.Specification;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

/**
 * 通用 Specification：根据 DTO 中的非空字段自动构建查询条件
 * @param <T> 实体类型
 */
public class BaseSpecification<T> implements Specification<T> {

    private final transient BaseDTO criteria;

    public BaseSpecification(BaseDTO criteria) {
        this.criteria = criteria;
    }

    @Override
    public Predicate toPredicate(Root<T> root, CriteriaQuery<?> query, CriteriaBuilder criteriaBuilder) {
        List<Predicate> predicates = new ArrayList<>();

        if (criteria == null) {
            return criteriaBuilder.conjunction();
        }

        Field[] fields = criteria.getClass().getDeclaredFields();
        for (Field field : fields) {
            field.setAccessible(true);
            try {
                Object value = field.get(criteria);
                if (value != null) {
                    String fieldName = field.getName();

                    // 处理时间范围查询（如 startTime / endTime 约定）
                    if (fieldName.endsWith("Start") && value instanceof java.util.Date) {
                        String propertyName = fieldName.substring(0, fieldName.length() - 5);
                        predicates.add(criteriaBuilder.greaterThanOrEqualTo(
                                root.get(propertyName), (java.util.Date) value));
                    } else if (fieldName.endsWith("End") && value instanceof java.util.Date) {
                        String propertyName = fieldName.substring(0, fieldName.length() - 3);
                        predicates.add(criteriaBuilder.lessThanOrEqualTo(
                                root.get(propertyName), (java.util.Date) value));
                    }
                    // 字符串类型 → 模糊查询
                    else if (value instanceof String && !((String) value).isEmpty()) {
                        predicates.add(criteriaBuilder.like(
                                root.get(fieldName), "%" + value + "%"));
                    }
                    // 其他类型 → 精确匹配
                    else {
                        predicates.add(criteriaBuilder.equal(
                                root.get(fieldName), value));
                    }
                }
            } catch (IllegalAccessException e) {
                // ignore
            }
        }

        return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
    }
}
```

### 查询条件 DTO 基类

```java
import java.util.Date;

/**
 * 查询条件 DTO 基类
 * 用于 BaseSpecification 动态构建查询条件
 */
public abstract class BaseDTO {

    // 子类只需声明字段，BaseSpecification 自动处理
    // 示例：
    // private String name;           → LIKE '%xxx%'
    // private Integer status;        → =
    // private Date createTimeStart;  → >= createTime
    // private Date createTimeEnd;    → <= createTime
}
```

**约定规则：**

| DTO 字段值类型 | SQL 生成 |
|---------------|---------|
| `String` | `LIKE '%value%'`（模糊） |
| 数字/枚举/布尔 | `=` 精确匹配 |
| 以 `Start` 结尾的 Date | `>= column` |
| 以 `End` 结尾的 Date | `<= column` |
| `null` 或空字符串 | 忽略（不参与条件） |

也支持更精确的注解驱动的做法：可以在字段上定义 `@QueryType` 注解或在 DTO 中直接使用 Spring Data 的 `@Spec` 注解（Spring Data JPA 4.0+ 的支持可参考 [PredicateSpecification 文档](https://docs.spring.io/spring-data/jpa/reference/jpa/specifications.html#predicate-specification)）。

---

## 八、分页工具类

### 8.1 PageQuery — 分页请求参数

```java
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

/**
 * 分页查询参数
 */
public class PageQuery {

    /** 页码，从 1 开始 */
    private int pageNum = 1;

    /** 每页条数 */
    private int pageSize = 10;

    /** 排序字段 */
    private String sortBy;

    /** 排序方向 */
    private Sort.Direction sortDir = Sort.Direction.DESC;

    // getter / setter ...

    public Pageable toPageable() {
        if (sortBy != null && !sortBy.isEmpty()) {
            Sort sort = Sort.by(sortDir, sortBy);
            return PageRequest.of(pageNum - 1, pageSize, sort);
        }
        return PageRequest.of(pageNum - 1, pageSize);
    }
}
```

### 8.2 Pager — 分页结果封装

```java
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

/**
 * 通用分页结果
 */
public class Pager<T> {

    /** 当前页码 */
    private int pageNum;

    /** 总记录数 */
    private long total;

    /** 每页条数 */
    private int pageSize;

    /** 总页数 */
    private int totalPage;

    /** 数据行 */
    private List<T> rows;

    public Pager() {}

    public Pager(int pageNum, long total, int pageSize, int totalPage, List<T> rows) {
        this.pageNum = pageNum;
        this.total = total;
        this.pageSize = pageSize;
        this.totalPage = totalPage;
        this.rows = rows;
    }

    /**
     * 基于 Specification 执行分页查询
     * @param specification 查询条件
     * @param pageQuery     分页参数
     * @param repository    数据源
     */
    public static <T> Pager<T> query(Specification<T> specification,
                                      PageQuery pageQuery,
                                      BaseRepository<T, ?> repository) {
        Pageable pageable = pageQuery.toPageable();
        Page<T> page = repository.findAll(specification, pageable);

        Pager<T> pager = new Pager<>();
        pager.setPageNum(page.getNumber() + 1);
        pager.setPageSize(page.getSize());
        pager.setTotal(page.getTotalElements());
        pager.setTotalPage(page.getTotalPages());
        pager.setRows(page.getContent());
        return pager;
    }

    // getter / setter ...
}
```

---

## 九、异常处理与统一响应

### 9.1 CommonException — 业务异常

```java
/**
 * 通用业务异常
 */
public class CommonException extends RuntimeException {

    public CommonException(String message) {
        super(message);
    }

    public CommonException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### 9.2 Result — 统一响应体

```java
/**
 * 统一 API 响应
 */
public class Result<T> {

    private int code;
    private String message;
    private T data;

    private Result() {}

    public static <T> Result<T> success() {
        return success(null);
    }

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.code = 200;
        result.message = "success";
        result.data = data;
        return result;
    }

    public static <T> Result<T> error(int code, String message) {
        Result<T> result = new Result<>();
        result.code = code;
        result.message = message;
        return result;
    }

    // getter / setter ...
}
```

### 9.3 GlobalExceptionHandler — 全局异常处理

```java
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import jakarta.persistence.EntityNotFoundException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(CommonException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleCommonException(CommonException e) {
        return Result.error(400, e.getMessage());
    }

    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Result<Void> handleEntityNotFound(EntityNotFoundException e) {
        return Result.error(404, e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleException(Exception e) {
        return Result.error(500, "服务器内部错误: " + e.getMessage());
    }
}
```

---

## 十、Converter — 实体与 DTO 转换

使用 `mapstruct-plus` 实现零反射高性能转换。

```java
import io.github.linpeilie.Converter;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 实体 ↔ DTO 转换器包装
 * 底层使用 MapStruct-Plus 编译期生成的 getter/setter 代码
 */
@Component
public class Converter {

    private final io.github.linpeilie.Converter delegate;

    public Converter(io.github.linpeilie.Converter delegate) {
        this.delegate = delegate;
    }

    /**
     * 单个对象转换
     */
    public <S, T> T convert(S source, Class<T> targetClass) {
        if (source == null) return null;
        return delegate.convert(source, targetClass);
    }

    /**
     * 列表转换
     */
    public <S, T> List<T> convert(List<S> sources, Class<T> targetClass) {
        if (sources == null) return List.of();
        return delegate.convert(sources, targetClass);
    }

    /**
     * 将源对象属性合并到目标对象（用于 update 场景）
     */
    public <S, T> void update(S source, T target) {
        if (source != null && target != null) {
            delegate.convert(source, target);
        }
    }
}
```

### MapStruct-Plus 配置

MapStruct-Plus 基于编译期注解处理，无需额外编写 Mapper 接口。

只需要在启动类或配置类上启用：

```java
@SpringBootApplication
@MapperScan("io.github.linpeilie")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**转换规则**（自动约定的字段映射）：
- 同名字段自动映射（`entity.name` ↔ `dto.name`）
- 支持类型自动转换（`Long ↔ long`、`LocalDateTime ↔ Date` 等）
- 支持 `@Mapping` 和 `@AutoMapping` 注解自定义映射

---

## 十一、完整使用示例

### 11.1 实体类

```java
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "medicine")
public class Medicine {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    private String category;

    private BigDecimal price;

    private Integer stock;

    @Column(name = "create_time")
    private LocalDateTime createTime;

    // getter / setter ...
}
```

### 11.2 DTO

```java
public class MedicineDTO extends BaseDTO {

    private String id;
    private String name;
    private String category;
    private BigDecimal price;
    private Integer stock;
    private LocalDateTime createTime;
    private LocalDateTime createTimeStart;  // 查询条件：开始时间
    private LocalDateTime createTimeEnd;    // 查询条件：结束时间

    // getter / setter ...
}
```

### 11.3 Repository

```java
public interface MedicineRepository
        extends BaseRepository<Medicine, String>,
                ExtensibleRepository<Medicine, String> {
}
```

### 11.4 Service

```java
@Service
public class MedicineService extends BaseService<Medicine, String> {
}
```

### 11.5 Controller

```java
@RestController
@RequestMapping("/medicines")
public class MedicineController extends BaseController<Medicine, MedicineDTO, String> {

    @Override
    protected Class<MedicineDTO> getDtoClass() {
        return MedicineDTO.class;
    }
}
```

### 11.6 完整的 API 能力

启动应用后，自动获得以下端点：

```bash
### 新增
POST /medicines
Body: { "name": "阿莫西林", "category": "抗生素", "price": 12.5, "stock": 100 }

### 批量新增
POST /medicines/batch
Body: [{ "name": "布洛芬", ... }, { "name": "维生素C", ... }]

### 按 ID 查询
GET /medicines/{id}

### 修改
PUT /medicines/{id}
Body: { "name": "阿莫西林胶囊", "price": 15.0 }

### 按 ID 删除
DELETE /medicines/{id}

### 批量删除
DELETE /medicines/batch
Body: ["id1", "id2", "id3"]

### 分页查询
GET /medicines/page?pageNum=1&pageSize=20&sortBy=createTime&sortDir=desc

### 动态条件分页查询
POST /medicines/page/condition?pageNum=1&pageSize=10
Body: { "name": "西林", "category": "抗生素", "createTimeStart": "2026-01-01T00:00:00" }
```

---

## 十二、最佳实践与注意事项

### 12.1 何时使用本模式

| 适用场景 | 不适用场景 |
|---------|-----------|
| 标准 CRUD + 动态查询的 REST API | 复杂聚合查询（多表 join、报表） |
| 多个业务域结构相似的项目 | 每个业务域有完全不同的操作语义 |
| 快速原型/脚手架搭建 | 需要 CQRS 事件溯源等特殊架构 |
| 管理后台/内部系统 | 对端点语义有精确控制要求的公开 API |

### 12.2 扩展建议

1. **复杂业务重写具体方法** — 子类可以 override BaseService 中的任何方法，在通用逻辑之上添加特殊业务处理
2. **DTO 转换精细化** — 对于 DTO 字段与实体字段映射不同的情况，使用 MapStruct `@Mapping` 注解指定映射
3. **查询条件扩展** — 在 `BaseSpecification` 中加入对不同查询类型（`IN`、`BETWEEN`、`IS NULL`）的注解支持
4. **权限控制** — 在 BaseController 方法上添加 `@PreAuthorize` 注解，或通过 AOP 统一拦截
5. **缓存集成** — 在 BaseService 的 `queryById` 等方法上添加 `@Cacheable`，提升查询性能

### 12.3 与 Spring Data REST 的对比

| 维度 | 本模式 | Spring Data REST |
|------|--------|-----------------|
| 控制粒度 | 完全可控，可重写任意方法 | 自动暴露 Repository 方法 |
| DTO 支持 | 原生支持任意 DTO | 默认暴露实体（需自定义投影） |
| 动态查询 | BaseSpecification 驱动 | 需编写 `@Query` 方法 |
| 事务边界 | Service 层明确控制 | Repository 层面隐藏控制 |
| 学习成本 | 中等 | 低（但灵活度受限） |

---

## 十三、知识关联

| 关联文档 | 关联点 |
|---------|--------|
| `spring/ai-agent/dan-vega-spring-ai-full-course-notes.md` | Dan Vega Spring AI 课程中的 JPA 最佳实践 |
| `ai-tools/spring-ai/from-assistants-to-agents-self-improving-agentic-systems.md` | Spring AI Agent 系统中的数据层设计 |
| `productivity/obsidian-vault-organization-full-course.md` | 代码组织方法论与项目结构设计 |

---

## 十四、参考资源

- [Spring Data JPA Reference: Specifications](https://docs.spring.io/spring-data/jpa/reference/jpa/specifications.html) — 官方 JPA 动态查询文档（含 4.0 的 PredicateSpecification）
- [Spring Data JPA Reference: Custom Implementations](https://docs.spring.io/spring-data/jpa/reference/repositories/custom-implementations.html) — Fragment 组合模式官方指南
- [MapStruct-Plus](https://github.com/linpeilie/mapstruct-plus-spring-boot-starter) — 高性能编译期 DTO 转换框架
- Spring Boot 3.5.0 · Spring Data JPA 3.x · Jakarta EE 11

---

*本文整合自 Spring Boot 实战案例合集付费内容及 Spring Data JPA 官方文档，经中文整理补充而成。*
