# Update Log

V0.1.0
========
- 严格来说，Redis事务并不一致；
- 使用Redis lua脚本实现Redis事务部分；

- Strictly speaking, Redis transactions are not consistent;
- Use Redis lua scripts to implement the Redis transaction part;

V0.0.7 - V0.0.8
========
- 基于Redis列表实现；
- 原子操作依赖Redis事务实现；
- 基于滑动窗口思想，实现后有令牌桶的味道；
- 可设置窗口大小、小窗口限制和小窗口数量；
  
- Realized based on Redis list;
- Atomic operation relies on Redis transaction to realize;
- Based on the idea of sliding window, it has the taste of token bucket after implementation;
- Window size and small window limit can be set and number of widgets;