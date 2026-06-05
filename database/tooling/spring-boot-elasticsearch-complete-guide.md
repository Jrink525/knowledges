---
title: "Spring Boot 整合 Elasticsearch 完全指南：从 0 到 1 实战"
tags:
  - spring-boot
  - elasticsearch
  - spring-data-elasticsearch
  - full-text-search
  - search-engine
  - backend
  - java
date: 2026-05-28
source: "整合自 Alexander Obregon (Medium), Shashi (Medium), cnblogs, 腾讯云开发者社区, Baeldung, Elastic 官方文档, abhishekranjandev (Medium) 等多篇技术博客"
---

# Spring Boot 整合 Elasticsearch 完全指南：从 0 到 1 实战

> **一句话总结**：本文从环境搭建到生产部署，完整覆盖 Spring Boot 整合 Elasticsearch 的每一步，包含基础 CRUD、复杂搜索、聚合分析、MySQL 双写同步、性能优化及排错指南。

---

## 目录

- [一、为什么选择 Elasticsearch？](#一为什么选择-elasticsearch)
- [二、核心概念速通](#二核心概念速通)
- [三、环境搭建与集群部署](#三环境搭建与集群部署)
- [四、Spring Boot 项目初始化](#四spring-boot-项目初始化)
- [五、数据模型与 Mapping 设计](#五数据模型与-mapping-设计)
- [六、Repository 层开发（基础 CRUD）](#六repository-层开发基础-crud)
- [七、NativeSearchQuery 高级查询](#七nativesearchquery-高级查询)
- [八、MySQL + ES 双写架构与数据同步](#八mysql--es-双写架构与数据同步)
- [九、聚合分析与搜索建议](#九聚合分析与搜索建议)
- [十、性能优化最佳实践](#十性能优化最佳实践)
- [十一、生产环境集群管理与监控](#十一生产环境集群管理与监控)
- [十二、十大常见问题与排查](#十二十大常见问题与排查)
- [十三、完整实战：电商商品搜索系统](#十三完整实战电商商品搜索系统)
- [十四、版本兼容速查与参考](#十四版本兼容速查与参考)

---

## 一、为什么选择 Elasticsearch？

### 1.1 传统数据库搜索的痛点

```sql
-- 传统 SQL LIKE 搜索
SELECT * FROM products
WHERE name LIKE '%手机%'
   OR description LIKE '%智能手机%'
   OR tags LIKE '%电子设备%';
```

| 痛点 | 说明 |
|------|------|
| **性能瓶颈** | `LIKE` 查询无法使用索引，数据量大时性能急剧下降 |
| **功能单一** | 不支持相关性评分、分词、同义词、模糊匹配等 |
| **扩展困难** | 数据库水平扩展复杂，无法应对海量数据场景 |
| **缺乏排名** | 无法按"相关性"对结果排序 |

### 1.2 Elasticsearch 的核心优势

- **近实时搜索**：数据写入后几乎立即可查
- **分布式架构**：轻松水平扩展，支持 PB 级数据
- **丰富的查询 DSL**：全文搜索、模糊查询、范围查询、地理查询、布尔组合
- **倒排索引**：基于 Lucene，搜索性能数倍于传统数据库
- **强大聚合**：支持多维度数据统计和分析
- **高可用**：自动分片 + 副本机制

### 1.3 适用场景对照

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 事务性操作 | MySQL / PostgreSQL | ACID 事务保证 |
| 简单查询 | 传统数据库 | 开发简单，资源消耗小 |
| **复杂搜索 / 全文检索** | **Elasticsearch** | 高性能，功能丰富 |
| 日志分析 | ELK Stack | 端到端解决方案 |
| 实时分析 | ClickHouse / Druid | 列式存储优化 |

---

## 二、核心概念速通

### 2.1 关系型数据库 ↔ ES 概念映射

| Elasticsearch | 关系型数据库 | 说明 |
|--------------|-------------|------|
| **Index**（索引） | Database（数据库） | 数据集合的容器 |
| Type（类型） | Table（表） | **7.x 后已废弃**，使用 `_doc` |
| **Document**（文档） | Row（行） | 基本数据单元，JSON 格式 |
| **Field**（字段） | Column（列） | 数据字段 |
| **Mapping**（映射） | Schema（模式） | 数据结构定义 |
| **Shard**（分片） | 分区 | 数据分片，支持分布式 |
| **Replica**（副本） | 备份 | 数据副本，保证高可用 |

### 2.2 倒排索引原理（性能之魂）

**数据库正排索引：**
```
文档 ID → 文档内容
1 → "SpringBoot实战教程"
2 → "Elasticsearch深入理解"
```

**Elasticsearch 倒排索引：**
```
关键词 → 文档 ID 列表
"SpringBoot"  → [1]
"实战"       → [1]
"教程"       → [1]
"Elasticsearch" → [2]
"深入"       → [2]
"理解"       → [2]
```

倒排索引将"文档 → 词"的关系反转为"词 → 文档"，搜索时直接查词即可快速定位所有包含该词的文档，无需全表扫描。这是 ES 高性能搜索的基石。

### 2.3 分析器（Analyzer）

```
输入文本 → 字符过滤器（Character Filter） → 分词器（Tokenizer） → 词元过滤器（Token Filter）
```

| 组件 | 作用 | 示例 |
|------|------|------|
| **Character Filter** | 预处理字符 | 去除 HTML 标签、替换特殊符号 |
| **Tokenizer** | 分词 | `standard`（英文）、`ik_max_word`（中文最细粒度） |
| **Token Filter** | 后处理 | 小写化、停用词、同义词 |

---

## 三、环境搭建与集群部署

### 3.1 Docker 单机快速部署（推荐）

```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - elastic

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - elastic

volumes:
  es_data:

networks:
  elastic:
    driver: bridge
```

```bash
# 启动
docker-compose up -d

# 验证
curl -X GET "localhost:9200/_cat/health?v"
```

**ES 8.x 安全注意事项**：如果启用 `xpack.security`，需要生成并记录初始密码：
```bash
docker logs elasticsearch | grep "Password for the elastic user"
```

### 3.2 Elasticsearch 8 使用 HTTPS 和密码的场景

```yaml
# docker-compose.yml（带安全配置）
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=true
      - xpack.security.authc.api_key.enabled=true
      - ELASTIC_PASSWORD=your_password
```

**Spring Boot 配置**：
```yaml
spring:
  elasticsearch:
    uris: https://localhost:9200
    username: elastic
    password: your_password
    socket-timeout: 30s
    connection-timeout: 10s
```

> ⚠️ 连接 HTTPS ES 时需跳过证书验证或配置信任证书，详见 [SSL 配置章节](#121-连接报错-ssllock-protocol-或-handshake-exception)。

### 3.3 生产环境集群配置（3 节点）

```yaml
# elasticsearch.yml（节点 1）
cluster.name: production-cluster
node.name: node-1
node.roles: [master, data, ingest]
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["node1:9300", "node2:9300", "node3:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
```

### 3.4 Kibana Dev Tools 基础

打开 Kibana（默认 http://localhost:5601）→ Dev Tools，可以用 Console 直接发请求：

```json
# 查看集群健康
GET _cat/health?v

# 查看索引
GET _cat/indices?v

# 查看节点
GET _cat/nodes?v
```

---

## 四、Spring Boot 项目初始化

### 4.1 版本兼容性指南（重要！）

| Spring Boot | Spring Data Elasticsearch | Elasticsearch |
|-------------|--------------------------|---------------|
| 3.x | 5.x | 8.x |
| 2.7.x | 4.4.x | 7.17.x |
| 2.6.x | 4.3.x | 7.15.x |
| 2.5.x | 4.2.x | 7.12.x |

> ⚠️ 版本不匹配会导致 `NoNodeAvailableException` 或序列化错误。务必检查 [Spring Data Elasticsearch 版本矩阵](https://spring.io/projects/spring-data-elasticsearch#support)。

### 4.2 Maven 依赖

```xml
<!-- Spring Boot 3.x + ES 8.x -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- 仅在 Spring Boot 2.x 需要额外添加 REST Client -->
<!-- Spring Boot 3.x 已内置 -->
<dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-high-level-client</artifactId>
    <version>7.17.26</version>
</dependency>
```

### 4.3 application.yml 配置

```yaml
spring:
  elasticsearch:
    uris: http://localhost:9200
    connection-timeout: 10s
    socket-timeout: 30s
  data:
    elasticsearch:
      repositories:
        enabled: true
      auto-index-creation: true   # 是否自动创建索引

# 自定义 ES 索引名称
app:
  elasticsearch:
    index:
      product: "products"
      order: "orders"
```

**ES 8.x HTTPS + 用户名密码场景：**
```yaml
spring:
  elasticsearch:
    uris: https://localhost:9200
    username: elastic
    password: your_password
    socket-timeout: 30s
    connection-timeout: 10s
```

### 4.4 自定义 RestClient 配置（可选）

```java
@Configuration
public class ElasticsearchConfig {

    @Bean
    public ElasticsearchClient elasticsearchClient() {
        RestClient restClient = RestClient.builder(
            HttpHost.create("http://localhost:9200")
        ).build();

        return new ElasticsearchClient(restClient);
    }

    @Bean
    public ElasticsearchRestTemplate elasticsearchRestTemplate(
            ElasticsearchClient client) {
        return new ElasticsearchRestTemplate(client);
    }
}
```

---

## 五、数据模型与 Mapping 设计

### 5.1 基础实体注解

```java
@Document(indexName = "products")
public class Product {

    @Id
    private String id;

    @Field(type = FieldType.Text, analyzer = "ik_max_word", searchAnalyzer = "ik_smart")
    private String name;

    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String description;

    @Field(type = FieldType.Double)
    private Double price;

    @Field(type = FieldType.Keyword)
    private String category;

    @Field(type = FieldType.Date, format = DateFormat.date_time)
    private Date createTime;

    @Field(type = FieldType.Integer)
    private Integer stock;

    @Field(type = FieldType.Boolean)
    private Boolean isActive;

    @Field(type = FieldType.Nested)
    private List<Specification> specifications;

    // getters / setters / constructors
}
```

**`@Field` 类型选择：**

| `FieldType` | 用途 | 说明 |
|-------------|------|------|
| `Text` | 全文搜索字段 | 会被分词器分析，支持匹配查询 |
| `Keyword` | 精确匹配、聚合、排序 | 不分词，原样存储 |
| `Integer` / `Long` / `Double` | 数值字段 | 支持范围查询 |
| `Date` | 日期字段 | 格式可自定义 |
| `Nested` | 嵌套对象 | 保留对象间关系 |
| `Object` | 普通 JSON 对象 | 扁平化存储，不支持独立查询 |

### 5.2 嵌套对象

```java
public class Specification {
    @Field(type = FieldType.Keyword)
    private String key;

    @Field(type = FieldType.Keyword)
    private String value;

    // getters / setters
}
```

### 5.3 自定义 Mapping 配置（JSON 文件）

`resources/es-mappings/product-mapping.json`：
```json
{
  "properties": {
    "name": {
      "type": "text",
      "analyzer": "ik_max_word",
      "search_analyzer": "ik_smart",
      "fields": {
        "keyword": {
          "type": "keyword"
        },
        "pinyin": {
          "type": "text",
          "analyzer": "pinyin_analyzer"
        }
      }
    },
    "description": {
      "type": "text",
      "analyzer": "ik_max_word"
    },
    "price": {
      "type": "double"
    },
    "category": {
      "type": "keyword"
    },
    "createTime": {
      "type": "date",
      "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
    },
    "stock": {
      "type": "integer"
    },
    "specifications": {
      "type": "nested",
      "properties": {
        "key": { "type": "keyword" },
        "value": { "type": "keyword" }
      }
    }
  }
}
```

### 5.4 自定义 Settings（分词器配置）

`resources/es-settings/product-settings.json`：
```json
{
  "analysis": {
    "analyzer": {
      "pinyin_analyzer": {
        "tokenizer": "ik_smart",
        "filter": ["pinyin_filter"]
      }
    },
    "filter": {
      "pinyin_filter": {
        "type": "pinyin",
        "keep_first_letter": false,
        "keep_full_pinyin": true
      }
    }
  }
}
```

> ⚠️ `pinyin` 分词器是插件，需手动安装：`./bin/elasticsearch-plugin install analysis-pinyin`

### 5.5 关联外部 Mapping

```java
@Document(indexName = "products")
@Setting(settingPath = "/es-settings/product-settings.json")
@Mapping(mappingPath = "/es-mappings/product-mapping.json")
public class Product {
    // ...
}
```

> **控制自动索引创建：**
> ```yaml
> spring.data.elasticsearch.auto-index-creation=false  # 禁用后完全手动管理索引
> ```

---

## 六、Repository 层开发（基础 CRUD）

### 6.1 定义 Repository 接口

```java
public interface ProductRepository
        extends ElasticsearchRepository<Product, String> {

    // ---- 派生查询（方法名自动解析） ----

    // 精确查询
    List<Product> findByName(String name);

    List<Product> findByCategory(String category);

    // 价格区间
    List<Product> findByPriceBetween(Double min, Double max);

    // 多条件 AND
    List<Product> findByNameAndCategory(String name, String category);

    // 存在检查
    boolean existsByName(String name);

    // 计数
    long countByCategory(String category);

    // 删除
    void deleteByName(String name);

    // ---- 分页查询（Pageable 参数） ----

    Page<Product> findByName(String name, Pageable pageable);

    Page<Product> findByCategory(String category, Pageable pageable);

    // ---- @Query 注解 ----

    @Query("{\"match\": {\"name\": \"?0\"}}")
    Page<Product> searchByName(String name, Pageable pageable);

    @Query("""
        {"bool": {
            "must": [
                {"match": {"name": "?0"}},
                {"range": {"price": {"gte": ?1, "lte": ?2}}}
            ]
        }}
    """)
    List<Product> findByNameAndPriceRange(String name, Double min, Double max);
}
```

### 6.2 CRUD 操作完整示例

```java
@Service
public class ProductService {

    @Autowired
    private ProductRepository repository;

    // 创建 / 更新
    public Product save(Product product) {
        if (product.getId() == null) {
            product.setId(UUID.randomUUID().toString());
        }
        return repository.save(product);
    }

    // 批量保存
    public Iterable<Product> saveAll(List<Product> products) {
        return repository.saveAll(products);
    }

    // 按 ID 查询
    public Optional<Product> findById(String id) {
        return repository.findById(id);
    }

    // 查询全部（分页）
    public Page<Product> findAll(int page, int size) {
        return repository.findAll(PageRequest.of(page, size));
    }

    // 删除
    public void deleteById(String id) {
        repository.deleteById(id);
    }

    // 条件查询
    public List<Product> findByCategory(String category) {
        return repository.findByCategory(category);
    }
}
```

### 6.3 派生方法命名规范速查

| 方法命名模式 | 生成的 ES 查询 |
|-------------|---------------|
| `findByName` | `term` 查询（Keyword）或 `match`（Text） |
| `findByNameAndPrice` | `bool` + `must` 组合 |
| `findByNameOrDescription` | `bool` + `should` |
| `findByPriceBetween` | `range` 查询 |
| `findByNameContaining` | `match_phrase_prefix` |
| `findByNameNot` | `bool` + `must_not` |
| `findByPriceLessThanEqual` | `range` + `lte` |
| `findByCreateTimeAfter` | `range` + `gt` |

> **完整关键字参考**：`And`、`Or`、`Is`、`Not`、`Between`、`LessThan`、`GreaterThan`、`After`、`Before`、`Like`、`Containing`、`In`、`NotIn`、`OrderBy`、`Exists`、`True`、`False`、`IgnoreCase`

---

## 七、NativeSearchQuery 高级查询

派生方法无法覆盖复杂场景时，使用 `ElasticsearchRestTemplate` + `NativeSearchQueryBuilder`。

### 7.1 基础设置

```java
@Service
public class ProductSearchService {

    @Autowired
    private ElasticsearchRestTemplate template;

    // 工具方法：将 SearchHits 转为 List
    private <T> List<T> toList(SearchHits<T> hits) {
        return hits.getSearchHits().stream()
                .map(SearchHit::getContent)
                .collect(Collectors.toList());
    }
}
```

### 7.2 全文搜索（Multi-match）

```java
public List<Product> fullTextSearch(String keyword) {
    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.multiMatchQuery(keyword)
                    .field("name", 3.0f)      // 加权：name 字段权重 3 倍
                    .field("description", 1.0f) // description 字段权重 1 倍
                    .operator(Operator.AND))    // 所有词都要出现
            .build();

    return toList(template.search(query, Product.class));
}
```

### 7.3 布尔组合查询（Bool Query）

```java
public List<Product> boolSearch(String keyword, Double minPrice,
                                Double maxPrice, String category) {
    BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();

    // must = AND（参与评分）
    if (StringUtils.hasText(keyword)) {
        boolQuery.must(QueryBuilders.matchQuery("name", keyword));
    }

    // filter = 过滤（不参与评分，可缓存，性能更好）
    if (minPrice != null || maxPrice != null) {
        RangeQueryBuilder range = QueryBuilders.rangeQuery("price");
        if (minPrice != null) range.gte(minPrice);
        if (maxPrice != null) range.lte(maxPrice);
        boolQuery.filter(range);
    }

    // filter + term（精确过滤，不走评分）
    if (StringUtils.hasText(category)) {
        boolQuery.filter(QueryBuilders.termQuery("category", category));
    }

    // must_not = NOT
    boolQuery.mustNot(QueryBuilders.matchQuery("status", "deleted"));

    // should = OR（提高匹配文档的评分）
    boolQuery.should(QueryBuilders.matchQuery("tags", "hot"));

    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(boolQuery)
            .withPageable(PageRequest.of(0, 20))
            .withSort(SortBuilders.scoreSort().order(SortOrder.DESC)) // 按相关性排序
            .build();

    return toList(template.search(query, Product.class));
}
```

**Bool Query 关键区别：**

| 子句 | 作用 | 是否参与评分 | 是否可缓存 |
|------|------|:----------:|:---------:|
| `must` | 必须匹配 | ✅ | ❌ |
| `mustNot` | 必须不匹配 | ❌ | ✅ |
| `filter` | 必须匹配 | ❌ | ✅ |
| `should` | 可选匹配 | 条件性 | ❌ |

> **最佳实践**：筛选条件（价格范围、分类、状态）用 `filter`，充分利用 Elasticsearch 的过滤器缓存。

### 7.4 高亮显示（Highlight）

```java
public SearchHits<Product> searchWithHighlight(String keyword) {
    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.multiMatchQuery(keyword, "name", "description"))
            .withHighlightFields(
                    new HighlightBuilder.Field("name")
                            .preTags("<em class='highlight'>")
                            .postTags("</em>"),
                    new HighlightBuilder.Field("description")
                            .preTags("<em class='highlight'>")
                            .postTags("</em>")
            )
            .build();

    return template.search(query, Product.class);
}
```

**前端渲染高亮：**
```java
// 提取高亮片段
SearchHit<Product> hit = ...;
Map<String, List<String>> highlights = hit.getHighlightFields();
String highlightedName = highlights.getOrDefault("name", List.of(hit.getContent().getName()))
        .stream().collect(Collectors.joining("..."));
```

### 7.5 分页与排序

```java
public Page<Product> searchWithPagination(String keyword, int page, int size,
                                          String sortField, SortOrder order) {
    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.matchQuery("name", keyword))
            .withPageable(PageRequest.of(page, size))
            .withSort(SortBuilders.fieldSort(sortField).order(order))
            .withSort(SortBuilders.scoreSort().order(SortOrder.DESC)) // 二级排序
            .build();

    SearchHits<Product> searchHits = template.search(query, Product.class);
    SearchPage<Product> searchPage = SearchHitSupport.searchPage(searchHits, query.getPageable());
    return searchPage.map(SearchHit::getContent);
}
```

### 7.6 Search After 深度分页

`from + size` 分页在**深度页（>10000）** 时性能骤降，使用 `search_after` 解决：

```java
public List<Product> searchAfter(String keyword, Object[] searchAfter,
                                 int size) {
    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.matchQuery("name", keyword))
            .withPageable(PageRequest.of(0, size)) // 始终从 0 开始
            .withSort(SortBuilders.fieldSort("createTime").order(SortOrder.DESC))
            .withSort(SortBuilders.fieldSort("_id").order(SortOrder.ASC)) // 唯一排序
            .build();

    if (searchAfter != null) {
        query.setSearchAfter(searchAfter);
    }

    SearchHits<Product> hits = template.search(query, Product.class);
    return hits.getSearchHits().stream()
            .map(SearchHit::getContent)
            .collect(Collectors.toList());
}
```

---

## 八、MySQL + ES 双写架构与数据同步

### 8.1 双库双实体模式（推荐）

MySQL 作为**主数据源**，ES 作为**搜索索引**，各自独立实体。

```java
// === MySQL Entity ===
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String description;
    private Double price;
    private String category;
    // ...
}

// === ES Entity ===
@Document(indexName = "products")
public class ProductIndex {
    @Id
    private String id;              // 对应 MySQL 的 id.toString()
    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String name;
    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String description;
    @Field(type = FieldType.Double)
    private Double price;
    @Field(type = FieldType.Keyword)
    private String category;
    // ...
}
```

### 8.2 同步写入模式（简单直接）

```java
@Service
@Transactional
public class ProductService {

    @Autowired
    private ProductRepository mysqlRepo;       // JPA Repository

    @Autowired
    private ProductIndexRepository esRepo;    // ES Repository

    public Product saveProduct(Product product) {
        // 1. 写入 MySQL（事务保证）
        Product saved = mysqlRepo.save(product);

        // 2. 同步写入 ES
        esRepo.save(toIndex(saved));

        return saved;
    }

    public void deleteProduct(Long id) {
        mysqlRepo.deleteById(id);
        esRepo.deleteById(id.toString());
    }

    private ProductIndex toIndex(Product p) {
        ProductIndex idx = new ProductIndex();
        idx.setId(p.getId().toString());
        idx.setName(p.getName());
        idx.setDescription(p.getDescription());
        idx.setPrice(p.getPrice());
        idx.setCategory(p.getCategory());
        return idx;
    }
}
```

### 8.3 异步同步 + 补偿机制（生产推荐）

```java
@Service
@Transactional
public class ProductServiceWithRetry {

    @Autowired
    private ProductRepository mysqlRepo;

    @Autowired
    private ProductIndexRepository esRepo;

    @Autowired
    private RetryService retryService;

    public Product saveProduct(Product product) {
        Product saved = mysqlRepo.save(product);

        // 异步同步 ES（失败后补偿）
        syncToEsAsync(saved);

        return saved;
    }

    @Async
    public void syncToEsAsync(Product product) {
        try {
            esRepo.save(toIndex(product));
        } catch (Exception e) {
            log.error("ES 同步失败，加入重试队列: {}", product.getId(), e);
            retryService.scheduleRetry(product.getId(), "SYNC_PRODUCT");
        }
    }

    private ProductIndex toIndex(Product p) { /* 转换逻辑 */ }
}
```

> ⚠️ **事务陷阱**：如果 `productRepository.save()` 抛出异常，ES 的 `save()` 不会回滚。生产环境推荐**先写 MySQL，异步刷 ES**，配合补偿重试。

### 8.4 基于 Canal 的实时同步（大规模场景）

```
MySQL binlog → Canal → MQ → 消费者同步到 ES
```

```java
@Component
public class CanalSyncHandler {

    @EventListener
    public void handleCanalEvent(CanalEvent event) {
        if (!"products".equals(event.getTableName())) return;

        switch (event.getEventType()) {
            case INSERT, UPDATE ->
                productIndexRepository.save(convert(event.getData()));
            case DELETE ->
                productIndexRepository.deleteById(event.getData().get("id"));
        }
    }
}
```

### 8.5 定时全量重建索引

```java
@Component
public class IndexRebuildJob {

    @Autowired private ProductRepository mysqlRepo;
    @Autowired private ProductIndexRepository esRepo;

    @Scheduled(cron = "0 0 3 * * ?") // 每天凌晨 3 点
    public void rebuildIndex() {
        log.info("开始重建产品索引...");
        esRepo.deleteAll();                         // 清空旧索引
        List<Product> products = mysqlRepo.findAll();
        esRepo.saveAll(products.stream()
                .map(this::toIndex)
                .collect(Collectors.toList()));
        log.info("重建完成，共索引 {} 条记录", products.size());
    }

    private ProductIndex toIndex(Product p) { /* 转换逻辑 */ }
}
```

---

## 九、聚合分析与搜索建议

### 9.1 聚合统计

```java
@Service
public class ProductAggregationService {

    @Autowired
    private ElasticsearchRestTemplate template;

    public AggregatedPage<Product> categoryAggregation() {
        NativeSearchQuery query = new NativeSearchQueryBuilder()
                .withQuery(QueryBuilders.matchAllQuery())
                .addAggregation(AggregationBuilders.terms("by_category")
                        .field("category.keyword")   // Keyword 字段才能聚合
                        .size(20)                    // 返回前 20 个分类
                        .subAggregation(AggregationBuilders.avg("avg_price")
                                .field("price"))
                        .subAggregation(
                                AggregationBuilders.stats("price_stats")
                                        .field("price"))
                )
                .addAggregation(AggregationBuilders.histogram("price_histogram")
                        .field("price")
                        .interval(500.0))
                .build();

        return template.queryForPage(query, Product.class);
    }
}
```

**解析聚合结果：**

```java
public void printAggregationResult(AggregatedPage<Product> page) {
    Terms terms = page.getAggregations().get("by_category");
    for (Terms.Bucket bucket : terms.getBuckets()) {
        String category = bucket.getKeyAsString();
        long count = bucket.getDocCount();

        // 子聚合
        Avg avgPrice = bucket.getAggregations().get("avg_price");
        Stats stats = bucket.getAggregations().get("price_stats");

        System.out.printf("分类: %s, 数量: %d, 均价: %.2f%n",
                category, count, avgPrice.getValue());
    }
}
```

### 9.2 搜索建议 / 自动补全（Completion Suggester）

首先在 Mapping 中定义 suggest 字段：

```java
public class ProductIndex {
    // ... 其他字段

    @Field(type = FieldType.Search_As_You_Type)
    private String nameSuggest;  // 基于输入即搜索

    @CompletionField(analyzer = "ik_max_word", searchAnalyzer = "ik_smart")
    private Completion suggest;  // 基于前缀建议
}
```

```java
public List<String> getSearchSuggestions(String prefix) {
    CompletionSuggestionBuilder suggestion = SuggestBuilders
            .completionSuggestion("suggest")
            .prefix(prefix, Fuzziness.ONE)  // 支持模糊
            .skipDuplicates(true)
            .size(10);

    SuggestBuilder suggestBuilder = new SuggestBuilder()
            .addSuggestion("product_suggest", suggestion);

    NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withSuggestBuilder(suggestBuilder)
            .build();

    SearchHits<ProductIndex> hits = template.search(query, ProductIndex.class);
    return hits.getSuggestResponse().getSuggestion("product_suggest")
            .getEntries().stream()
            .flatMap(entry -> entry.getOptions().stream())
            .map(option -> option.getText().string())
            .collect(Collectors.toList());
}
```

### 9.3 同义词搜索

```json
{
  "settings": {
    "analysis": {
      "filter": {
        "my_synonym": {
          "type": "synonym",
          "synonyms": [
            "手机, 智能手机, 移动电话, cellular phone",
            "电脑, 计算机, 笔记本, laptop",
            "降价, 打折, 促销, 优惠"
          ]
        }
      },
      "analyzer": {
        "my_analyzer": {
          "tokenizer": "ik_max_word",
          "filter": ["my_synonym"]
        }
      }
    }
  }
}
```

搜索"手机"会自动匹配包含"智能手机"、"移动电话"、"cellular phone"的文档。

---

## 十、性能优化最佳实践

### 10.1 批量操作（Bulk API）

```java
public void bulkIndex(List<ProductIndex> products) {
    List<IndexQuery> queries = products.stream()
            .map(p -> new IndexQueryBuilder()
                    .withId(p.getId())
                    .withObject(p)
                    .build())
            .collect(Collectors.toList());

    template.bulkIndex(queries, BulkOptions.defaultOptions());
}
```

**批量大小建议：** 5,000–15,000 条或 5–15 MB，需要根据实际情况测试。

### 10.2 Filter 优先于 Query

```java
// ❌ 差的做法（所有条件都评分）
boolQuery.must(QueryBuilders.termQuery("category", "电子产品"));
boolQuery.must(QueryBuilders.rangeQuery("price").gte(100));

// ✅ 好的做法（筛选条件用 filter，利用缓存）
boolQuery.must(QueryBuilders.matchQuery("name", keyword));   // 评分
boolQuery.filter(QueryBuilders.termQuery("category", "电子产品")); // 缓存
boolQuery.filter(QueryBuilders.rangeQuery("price").gte(100));     // 缓存
```

### 10.3 字段映射优化

```
慢：name   → type: text（全文搜索+排序时都要 fielddata）
     排序用 name.keyword（keyword 子字段）

快：name   → type: text（仅搜索）
     name_sort → type: keyword（仅排序，doc_values 启用）

不需要搜索的字段 → "index": false
不需要聚合的字段 → "doc_values": false
```

### 10.4 缩减返回字段

```java
NativeSearchQuery query = new NativeSearchQueryBuilder()
        .withQuery(QueryBuilders.matchAllQuery())
        .withFields("id", "name", "price")  // 只返回需要的字段
        .build();
```

### 10.5 索引刷新策略

```yaml
# 批量导入时临时调整
PUT /products/_settings
{
  "index": {
    "refresh_interval": "-1",       # 停用自动刷新
    "number_of_replicas": 0          # 停用副本（导入完成后恢复）
  }
}

# 导入完成后恢复
PUT /products/_settings
{
  "index": {
    "refresh_interval": "1s",        # ES 8.x 默认
    "number_of_replicas": 1
  }
}
```

### 10.6 JVM 内存调优

```yaml
# docker-compose 环境变量
ES_JAVA_OPTS: "-Xms4g -Xmx4g"
```

> **黄金法则**：ES 堆内存 ≤ 物理内存的 50%，且 ≤ 32GB（超过 32GB JVM 指针压缩失效）。

### 10.7 查询性能总结速查

| 优化手段 | 效果 | 适用场景 |
|---------|:---:|---------|
| 用 `filter` 代替 `must` | ⭐⭐⭐ | 筛选条件 |
| 限制返回字段 | ⭐⭐ | 大文档查询 |
| 使用 `search_after` 代替深分页 | ⭐⭐⭐ | 滚动翻页 |
| 批量导入时取消副本和刷新 | ⭐⭐⭐ | 数据初始化 |
| `keyword` 避免 `text` 做聚合 | ⭐⭐⭐ | 分组统计 |
| 开启慢查询日志 | ⭐⭐ | 性能排查 |
| 预热文件系统缓存 | ⭐⭐ | 冷启动 |

---

## 十一、生产环境集群管理与监控

### 11.1 健康检查集成

```java
@Component
public class ElasticsearchHealthIndicator implements HealthIndicator {

    @Autowired
    private ElasticsearchRestTemplate template;

    @Override
    public Health health() {
        try {
            var clusterHealth = template.cluster().health();
            var status = clusterHealth.status();

            if (status == ClusterHealthStatus.RED) {
                return Health.down()
                        .withDetail("cluster_status", "RED")
                        .withDetail("nodes", clusterHealth.numberOfNodes())
                        .withDetail("active_shards", clusterHealth.activeShards())
                        .build();
            }

            return Health.up()
                    .withDetail("cluster_status", status.name())
                    .withDetail("nodes", clusterHealth.numberOfNodes())
                    .withDetail("active_shards", clusterHealth.activeShards())
                    .build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

### 11.2 慢查询监控

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, metrics, elasticsearch
```

```java
@Component
@Slf4j
public class SlowQueryMonitor {

    @EventListener
    public void monitorSlowQuery(SearchQueryEvent event) {
        if (event.getExecutionTime() > 1000) { // 超过 1 秒
            log.warn("慢查询检测: {}, 执行时间: {}ms",
                    event.getQuery(), event.getExecutionTime());
        }
    }
}
```

### 11.3 ES 服务端慢日志配置

```json
PUT /products/_settings
{
  "index.search.slowlog.threshold.query.warn": "10s",
  "index.search.slowlog.threshold.query.info": "5s",
  "index.search.slowlog.threshold.query.debug": "2s",
  "index.search.slowlog.threshold.query.trace": "500ms",
  "index.indexing.slowlog.threshold.index.warn": "10s",
  "index.indexing.slowlog.threshold.index.info": "5s",
  "index.indexing.slowlog.threshold.index.debug": "2s",
  "index.indexing.slowlog.threshold.index.trace": "500ms"
}
```

---

## 十二、十大常见问题与排查

### 12.1 连接报错 SSL/Lock Protocol

**错误：** `javax.net.ssl.SSLHandshakeException` 或 `not a valid locked protocol`

**原因：** ES 8.x 默认开启 HTTPS，但 Spring Boot 配置了 HTTP。

**解决：**
```yaml
# 方案 A：配置 Spring Boot 用 HTTPS
spring:
  elasticsearch:
    uris: https://localhost:9200
    username: elastic
    password: your-password
    socket-timeout: 30s
    connection-timeout: 10s
```

```yaml
# 方案 B：关闭 ES 安全（仅开发环境）
# docker-compose 环境变量
xpack.security.enabled: false
```

```java
// 方案 C：自定义 Client 跳过 SSL 验证（测试用）
@Bean
public ElasticsearchClient elasticsearchClient() {
    RestClientBuilder builder = RestClient.builder(
            HttpHost.create("https://localhost:9200"))
            .setHttpClientConfigCallback(cb -> {
                try {
                    SSLContext sslContext = SSLContext.getInstance("TLS");
                    sslContext.init(null, new TrustManager[]{
                            new X509TrustManager() {
                                public X509Certificate[] getAcceptedIssuers() { return null; }
                                public void checkClientTrusted(X509Certificate[] certs, String authType) {}
                                public void checkServerTrusted(X509Certificate[] certs, String authType) {}
                            }
                    }, new java.security.SecureRandom());
                    cb.setSSLContext(sslContext)
                      .setSSLHostnameVerifier(NoopHostnameVerifier.INSTANCE);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
                return cb;
            });
    return new ElasticsearchClient(builder.build());
}
```

### 12.2 NoNodeAvailableException

**可能原因：**
1. ES 服务未启动或端口不对
2. 版本不匹配（ES 7.x ↔ Spring Data ES 5.x）
3. 网络/防火墙问题

**排查：**
```bash
curl -X GET "http://localhost:9200/"    # 确认 ES 可达
curl -X GET "http://localhost:9200/_cat/indices?v"
```

### 12.3 Mapping 冲突

**错误：** `illegal_argument_exception: mapper [xxx] cannot be changed from type [text] to [keyword]`

**原因：** 字段类型已存在且无法修改。

**解决：** 创建新索引并 reindex：
```json
PUT /products_v2
{
  "mappings": { "properties": { "price": { "type": "double" } } }
}

POST /_reindex
{
  "source": { "index": "products" },
  "dest":   { "index": "products_v2" }
}

# 确认后删除旧索引并创建别名
DELETE /products
PUT /products_v2/_alias/products
```

### 12.4 数据不一致（MySQL 有但 ES 没有）

**原因：** 双写模式下，MySQL 写入成功，ES 写入因网络/异常失败。

**解决：**
1. 加入**重试队列**（Redis / DB + 定时任务）
2. 每日定时**全量重建**索引（凌晨低峰期）
3. 引入 Canal/Kafka 实现**binlog 实时同步**

### 12.5 搜索结果不准确（中文分词）

**原因：** 未安装 `ik` 中文分词器，使用了默认 `standard` 分词器。

**验证：**
```json
POST /_analyze
{
  "analyzer": "standard",
  "text": "智能手机"
}
// standard 输出: "智", "能", "手", "机" ← 错误
```

**解决方案：** 安装 `analysis-ik` 插件：
```bash
./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.8.0/elasticsearch-analysis-ik-8.8.0.zip
```

验证：
```json
POST /_analyze
{
  "analyzer": "ik_max_word",
  "text": "智能手机"
}
// ik_max_word 输出: "智能手机", "智能", "手机" ← 正确
```

### 12.6 聚合失败：Fielddata is disabled

**错误：** `Text fields are not optimised for operations that require per-document field data`

**原因：** 对 `text` 类型字段做了聚合或排序。

**解决：**
```java
// 使用 keyword 子字段
@Field(type = FieldType.Text)
private String name;

// 聚合时用 name.keyword
AggregationBuilders.terms("by_name").field("name.keyword");
```

或者定义显式子字段：
```json
"name": {
  "type": "text",
  "fields": {
    "keyword": { "type": "keyword" }
  }
}
```

### 12.7 结果总数超过 10000 不准确

**原因：** ES `track_total_hits` 默认为 10000。

**解决：**
```java
NativeSearchQuery query = new NativeSearchQueryBuilder()
        .withQuery(QueryBuilders.matchAllQuery())
        .withTrackTotalHits(true)  // 精确计数
        .build();
```

或全局设置：
```java
query.setTrackTotalHits(true);
query.setTrackTotalHitsUpTo(Integer.MAX_VALUE);
```

### 12.8 批量导入太慢

```java
// 批量导入时：
// 1. 临时调大 refresh interval
// 2. 临时关闭副本
// 3. 使用 Bulk API（不是逐条 save）
// 4. 适当增大 bulk 大小（测试 5000-10000 为基准）
```

### 12.9 ES 突然返回空结果

**可能原因：**
- 索引被删除
- 索引别名被切换
- 查询条件过滤了所有结果
- 分片未分配（集群健康非 green）

**排查：**
```bash
GET _cat/shards?v    # 查看分片状态
GET _cat/indices?v   # 查看索引是否存在
```

### 12.10 内存和 GC 问题

**症状：** 频繁 Full GC、查询变慢、节点掉线

**排查：**
```bash
# ES API
GET _nodes/stats/jvm
GET _cat/health?v
```

**常见原因与解决：**

| 原因 | 解决方案 |
|------|---------|
| 堆内存过大（>32GB） | 单节点 ≤ 32GB |
| 堆内存占总内存 >50% | 降低堆内存占比 |
| 查询返回太多数据 | 限制返回字段数 + 分页 |
| 聚合 on 高基数 field | 限制聚合 size, 用 `composite` 聚合 |
| 未关闭的 scroll context | 确保用完后 clear scroll |

---

## 十三、完整实战：电商商品搜索系统

### 13.1 需求分析

构建一个电商商品搜索系统，支持：

1. **关键词搜索** — 支持中文分词、拼音搜索
2. **多维度筛选** — 价格范围、品牌、分类
3. **排序** — 综合、价格升/降、销量
4. **聚合统计** — 分类统计、价格分布
5. **搜索建议** — 自动补全
6. **高亮显示** — 搜索结果关键词高亮

### 13.2 技术架构

```
前端页面 → Spring Boot 应用集群 → Elasticsearch 集群
             ↓
           MySQL（主数据源）
             ↓
         Canal/Kafka（实时同步到 ES）
```

### 13.3 完整搜索 Service

```java
@Service
@Slf4j
public class EcommerceSearchService {

    @Autowired
    private ElasticsearchRestTemplate template;

    /**
     * 综合搜索 API
     */
    public SearchResult<ProductIndex> search(SearchRequest req) {
        BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();

        // 1. 关键词搜索（多字段加权）
        if (StringUtils.hasText(req.getKeyword())) {
            MultiMatchQueryBuilder mmq = QueryBuilders
                    .multiMatchQuery(req.getKeyword(),
                            "name^3",          // 权重 3
                            "description^1",   // 权重 1
                            "category^2")      // 权重 2
                    .type(MultiMatchQueryBuilder.Type.BEST_FIELDS);
            boolQuery.must(mmq);
        }

        // 2. 过滤条件（用 filter，可缓存）
        if (req.getMinPrice() != null || req.getMaxPrice() != null) {
            RangeQueryBuilder rq = QueryBuilders.rangeQuery("price");
            if (req.getMinPrice() != null) rq.gte(req.getMinPrice());
            if (req.getMaxPrice() != null) rq.lte(req.getMaxPrice());
            boolQuery.filter(rq);
        }
        if (StringUtils.hasText(req.getCategory())) {
            boolQuery.filter(QueryBuilders.termQuery("category", req.getCategory()));
        }
        if (StringUtils.hasText(req.getBrand())) {
            boolQuery.filter(QueryBuilders.termQuery("brand", req.getBrand()));
        }

        NativeSearchQueryBuilder queryBuilder = new NativeSearchQueryBuilder()
                .withQuery(boolQuery);

        // 3. 高亮
        queryBuilder.withHighlightFields(
                new HighlightBuilder.Field("name")
                        .preTags("<span class='hl'>").postTags("</span>"),
                new HighlightBuilder.Field("description")
                        .preTags("<span class='hl'>").postTags("</span>")
        );

        // 4. 排序
        queryBuilder.withSort(buildSort(req.getSortBy(), req.getSortOrder()));

        // 5. 分页
        int page = Math.max(req.getPage(), 0);
        int size = Math.min(req.getSize(), 100); // 最大 100
        queryBuilder.withPageable(PageRequest.of(page, size));

        // 6. 聚合
        queryBuilder.addAggregation(AggregationBuilders.terms("categories")
                .field("category.keyword").size(20));
        queryBuilder.addAggregation(AggregationBuilders.histogram("price_ranges")
                .field("price").interval(500));
        queryBuilder.addAggregation(AggregationBuilders.avg("avg_price")
                .field("price"));

        // 执行
        SearchHits<ProductIndex> hits = template.search(
                queryBuilder.build(), ProductIndex.class);

        return buildResult(hits, req.getPage(), size);
    }

    private SortBuilder<?> buildSort(String sortBy, String order) {
        SortOrder dir = "desc".equalsIgnoreCase(order)
                ? SortOrder.DESC : SortOrder.ASC;
        return switch (sortBy) {
            case "price" -> SortBuilders.fieldSort("price").order(dir);
            case "sales" -> SortBuilders.fieldSort("salesCount").order(order);
            default -> SortBuilders.scoreSort().order(SortOrder.DESC); // 综合排序
        };
    }

    private SearchResult<ProductIndex> buildResult(
            SearchHits<ProductIndex> hits, int page, int size) {
        List<ProductIndex> products = hits.stream()
                .map(h -> {
                    ProductIndex p = h.getContent();
                    p.setHighlightFields(h.getHighlightFields());
                    return p;
                })
                .collect(Collectors.toList());

        long total = hits.getTotalHits();
        return new SearchResult<>(products, page, size, total);
    }
}
```

### 13.4 请求/响应 DTO

```java
@Data
public class SearchRequest {
    private String keyword;
    private Double minPrice;
    private Double maxPrice;
    private String category;
    private String brand;
    private String sortBy = "relevance";  // relevance, price, sales
    private String sortOrder = "desc";
    private int page = 0;
    private int size = 20;
}

@Data
@AllArgsConstructor
public class SearchResult<T> {
    private List<T> items;
    private int page;
    private int size;
    private long total;
}
```

### 13.5 Controller 层

```java
@RestController
@RequestMapping("/api/search")
public class SearchController {

    @Autowired
    private EcommerceSearchService searchService;

    @PostMapping("/products")
    public ResponseEntity<SearchResult<ProductIndex>> search(
            @RequestBody SearchRequest request) {
        return ResponseEntity.ok(searchService.search(request));
    }
}
```

### 13.6 curl 测试

```bash
# 搜索并高亮
curl -X POST http://localhost:8080/api/search/products \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "智能手机",
    "minPrice": 1000,
    "maxPrice": 8000,
    "category": "电子产品",
    "sortBy": "price",
    "sortOrder": "asc",
    "page": 0,
    "size": 20
  }'
```

---

## 十四、版本兼容速查与参考

### 14.1 Spring Boot / Spring Data ES / ES 兼容矩阵

| Spring Boot | Spring Data ES | ES | 状态 |
|-------------|---------------|:--:|:----:|
| 3.4.x | 5.4.x | 8.16.x | ✅ 当前 |
| 3.3.x | 5.3.x | 8.15.x | ✅ |
| 3.2.x | 5.2.x | 8.12.x | ✅ |
| 3.1.x | 5.1.x | 8.10.x | ✅ |
| 3.0.x | 5.0.x | 8.7.x | ✅ |
| 2.7.x | 4.4.x | 7.17.x | ⚠️ 维护模式 |
| 2.6.x | 4.3.x | 7.15.x | ❌ EOL |

### 14.2 关键配置参考

```yaml
# Spring Boot 3.x + ES 8.x 最小配置
spring:
  elasticsearch:
    uris: http://localhost:9200
    connection-timeout: 10s
    socket-timeout: 30s
```

```yaml
# Spring Boot 2.x + ES 7.x 配置
spring:
  data:
    elasticsearch:
      cluster-name: docker-cluster
      cluster-nodes: localhost:9300
      repositories:
        enabled: true
```

### 14.3 官方参考链接

- [Spring Data Elasticsearch 官方文档](https://docs.spring.io/spring-data/elasticsearch/docs/current/reference/html/)
- [Elasticsearch 官方参考](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [ES Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Spring Boot ES 指南](https://docs.spring.io/spring-boot/docs/current/reference/html/data.html#data.nosql.elasticsearch)
- [analysis-ik 插件](https://github.com/medcl/elasticsearch-analysis-ik)

> **引用来源：** 本文整合自 Alexander Obregon (Medium)、Shashi (Medium, Feb 2025)、cnblogs 实战教程、腾讯云开发者社区、Baeldung、Elastic 官方文档、abhishekranjandev (Medium) 等多篇技术博客。
