# Spring Boot Roadmap 完整内容

来源：[roadmap.sh/spring-boot](https://roadmap.sh/spring-boot)
爬取时间：2026-06-08

---

## 路线图结构

📌 **Introduction**
  ▸ Why Use Spring · Configuration · Authentication · Dependency Injection
📌 **Spring Security**
  ▸ Authorization · Spring IOC · OAuth2 · Spring AOP
📌 **Spring Boot Starters**
  ▸ Spring Bean Scope · Transactions · Relationships
📌 **Autoconfiguration**
  ▸ Spring Cloud Gateway · Entity Lifecycle
📌 **Actuators**
  ▸ Cloud Config
📌 **Embedded Server**
  ▸ Spring Cloud Circuit Breaker
📌 **Hibernate**
  ▸ Spring Data · Spring Data JPA
📌 **Spring Data**
  ▸ Spring Cloud
📌 **Microservices**
  ▸ Spring Data JDBC · Servlet · JPA Test · Mock MVC · JSP Files
📌 **Spring MVC**
  ▸ Architecture · Components
📌 **Testing**
  ▸ @SpringBootTest Annotation · @MockBean Annotation

---

## 各节点详情

### Introduction
Spring Boot is a framework for building applications based on the Spring Framework. It aims to make it easy to create stand-alone, production-grade Spring-based applications. Spring Boot provides an embedded application server, automatic configuration, pre-configured starters, and ease of packaging and distribution.

### Why Use Spring
Spring Boot provides:
- Embedded Application Server
- Automatic Configuration
- Pre-configured Starters
- Ease of Packaging and Distribution
- Ease of monitoring through built-in health monitoring

### Configuration (Spring Core)
Involves specifying the various configuration details required for an application to function properly, including setting up beans, specifying bean dependencies, configuring aspect-oriented programming (AOP), and setting up data access.

### Dependency Injection
Spring Boot uses Spring Framework's IoC container to manage objects and their dependencies. The IoC container is responsible for creating objects, wiring them together, and managing their lifecycle.

### Spring IOC
Inversion of Control (IoC) design pattern that inverts the flow of control in a program. Container manages the instantiation and lifecycle of objects. Objects are created with their dependencies already provided.

### Spring AOP (Aspect-Oriented Programming)
Allows developers to define behaviors ("aspects") that cut across multiple classes, such as logging or transaction management. These are called "advices" and can be applied to methods using pointcuts.

### Annotations
Commonly used annotations: `@SpringBootApplication`, `@RestController`, `@Autowired`, `@RequestMapping`, `@PathVariable`, `@Configuration`, `@Component`, `@Service`, `@Repository`, `@Transactional`, `@Value`, `@Profile`.

### Spring Bean Scope
Beans can have different scopes: Singleton (default), Prototype, Request (web), Session (web), Application (web), WebSocket (web).

### Terminology
Key concepts: **Beans** (Java objects managed by Spring), **IoC** (Spring managing bean lifecycles), **DI** (Spring injecting dependencies).

### Architecture
Spring Boot follows a layered architecture with four layers:
- **Presentation Layer**: handles HTTP requests, translates JSON parameters to objects
- **Business Layer**: handles all business logic, service layer, validation, authorization
- **Persistence Layer**: contains all database storage logic
- **Database Layer**: contains CRUD operations

### Spring Security
Framework for securing Java-based applications. Highly customizable authentication and access-control framework for web applications and RESTful web services.

### Authentication
Spring Security provides wide range of options including support for username/password, OAuth2, JWT, and more. Configurable via `AuthenticationManagerBuilder`.

### Authorization
Spring Security can authorize user's access to specific resources. Supports role-based and permission-based access control using annotations like `@PreAuthorize`, `@Secured`.

### OAuth2
Spring Security OAuth2 supports both authorization code grant type (web apps) and implicit grant type (single-page apps). Can also configure as OAuth2 resource server.

### JWT Authentication
Spring Security provides a JWT-based authentication filter. Checks the JWT in the request header, if valid it authenticates the user and creates a security context.

### Spring Boot Starters
Set of convenient dependency descriptors you can include in your application. Provide functionality like security, data access, web services. Include: spring-boot-starter-web, spring-boot-starter-data-jpa, spring-boot-starter-security, etc.

### Autoconfiguration
Powerful feature that makes it easy to configure beans based on the presence of certain dependencies and properties. Uses `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, etc.

### Actuators
Production-ready features for monitoring and managing your application. Provide endpoints exposing information about health, metrics, environment, beans, and more. Common endpoints: `/health`, `/metrics`, `/info`, `/env`, `/beans`.

### Embedded Server
Allows running a web server directly within your application without deploying to a separate standalone server. Supports Tomcat (default), Jetty, Undertow (reactive). Configuration via `application.properties`.

### Spring Data
Collection of projects for data access in Spring-based applications. Provides a common interface for relational databases, NoSQL data stores, and cloud-based data services. Simplifies data access with repository abstraction.

### Spring Data JPA
Library that makes it easy to implement JPA-based repositories. Provides CRUD operations, pagination, sorting, and custom queries. Key components: `JpaRepository`, `CrudRepository`, `PagingAndSortingRepository`.

### Hibernate
Java framework providing object-relational mapping from Java classes to database tables. Provides data querying and retrieval facility.

### Entity Lifecycle (Hibernate)
Entity passes through stages: Transient, Persistent, Detached, Removed. Managed by `EntityManager` with operations like `persist()`, `merge()`, `remove()`, `find()`.

### Transactions
Unit of work with ACID properties (Atomicity, Consistency, Isolation, Durability). Spring provides `@Transactional` annotation for declarative transaction management.

### Relationships (Hibernate)
Entity relationships: @OneToOne, @OneToMany, @ManyToOne, @ManyToMany. Foreign key relationships between tables for referential integrity.

### Microservices
Architectural style where a large application is built as a collection of small, independently deployable services. Spring Microservices framework makes it easier to build and manage.

### Spring Cloud
Collection of libraries and tools for building cloud-native applications. Provides abstractions for service discovery, configuration management, circuit breakers, and routing.

### Spring Cloud Gateway
Library for building API gateways. Acts as intermediary between application and microservices. Handles request routing, composition, protocol translation.

### Spring Cloud Circuit Breaker
Library for managing fault tolerance using Circuit Breaker pattern. Prevents cascading failures and improves resilience. Works with Resilience4j, Hystrix.

### Cloud Config
Library for managing configuration properties for distributed applications. Externalizes configuration properties. Provides a central server for managing config.

### Spring Cloud OpenFeign
Library for creating declarative REST clients. Makes HTTP requests to microservices without writing low-level code. Uses `@FeignClient` annotation.

### Eureka
Library for service discovery. Allows services to find and communicate without hardcoding addresses. Service registry with @EnableEurekaServer, @EnableEurekaClient.

### Micrometer
Vendor-neutral metrics collection library. Integrates with monitoring systems like Prometheus, Datadog, New Relic.

### Spring MVC
Framework for building web applications using Model-View-Controller design pattern. Components: Model (data), View (presentation), Controller (handles requests).

### Spring MVC Architecture
Components: DispatcherServlet (front controller), Controller classes, HandlerMapping, ViewResolver, ModelAndView, View.

### Components (Spring MVC)
Key components work together to handle requests: DispatcherServlet, Controller, HandlerMapping, ViewResolver, ModelAndView, View.

### Servlet
DispatcherServlet is the front controller in Spring-based web applications. Entry point for handling all web requests.

### JSP Files
Technology for building dynamic web pages using Java. In Spring MVC, view component is implemented using JSP files. Uses JSTL tags for logic.

### Testing
Spring provides testing utilities for controllers, services, repositories. Rich set of testing annotations.

### @SpringBootTest Annotation
Creates a fully-configured Spring ApplicationContext for testing. Used to test all components in a real application environment.

### @MockBean Annotation
Creates a mock implementation of a bean in the Spring application context. Replaces the original bean with a mock for testing.

### Mock MVC
Class that allows testing Spring MVC controllers without an actual web server. Part of Spring Test module. Works with `@WebMvcTest`.

### JPA Test
Spring JPA provides testing support for database operations. `@DataJpaTest` for JPA-specific testing with in-memory database.

### Cloud Config
(see above - Spring Cloud Config)
