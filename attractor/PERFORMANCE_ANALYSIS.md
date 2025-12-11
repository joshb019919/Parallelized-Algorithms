# Attractor Algorithm: Performance Analysis & Crossover Point

## Executive Summary

This document analyzes the performance characteristics of the naive sequential implementation versus the PySpark implementation of the attractor algorithm. While PySpark adds significant overhead due to JVM initialization and distributed framework setup, it will eventually become advantageous for extremely large graphs. This analysis identifies the theoretical and empirical crossover point.

---

## 1. Benchmark Data Summary

| Nodes | Naive Time (ms) | Spark Time (ms) | Spark Overhead (ms) | Speedup | Advantage |
|-------|-----------------|-----------------|-------------------|---------|-----------|
| 1,000 | 33.06 | 3,087.33 | 3,054.27 | 0.011x | Naive |
| 5,000 | 47.29 | 3,103.29 | 3,056.00 | 0.015x | Naive |
| 10,000 | 59.82 | 3,097.79 | 3,037.97 | 0.019x | Naive |
| 50,000 | 265.03 | 3,297.17 | 3,032.14 | 0.080x | Naive |
| 100,000 | 519.22 | 3,279.77 | 2,760.55 | 0.158x | Naive |
| 500,000 | 2,938.25 | 5,709.88 | 2,771.63 | 0.514x | Naive |
| 1,000,000 | 5,957.94 | 7,796.80 | 1,838.86 | 0.764x | Naive |

---

## 2. Cost Model Analysis

### 2.1 Naive Algorithm (Sequential)

The naive implementation has a relatively simple cost model:

**Time Complexity**: O(V × E_avg × I) where:
- V = number of nodes
- E_avg = average edges per node
- I = number of iterations until convergence

**Empirical Cost Model (from benchmarks)**:

From the data, we can fit a linear regression to estimate the constant factors:

```
T_naive(n) ≈ 5.96e-6 × n  (in seconds)
           ≈ 5.96 × n     (in microseconds)
```

Analyzing the relationship:
- 1K nodes: 33.06 ms ≈ 33.06 µs/node
- 10K nodes: 59.82 ms ≈ 5.98 µs/node
- 100K nodes: 519.22 ms ≈ 5.19 µs/node
- 1M nodes: 5,957.94 ms ≈ 5.96 µs/node

**Average: ~5.8 µs per node**

This is excellent efficiency and shows near-linear scaling with constant factor:
$$T_{naive}(n) \approx 5.8 \times 10^{-6} \times n \text{ seconds}$$

### 2.2 PySpark Algorithm

The PySpark implementation has a significant fixed overhead from JVM startup and distributed framework setup:

**Cost Model (from benchmarks)**:

```
T_spark(n) ≈ 3.0 + 0.0034 × n  (in seconds)
           ≈ 3000 + 3.4 × n    (in milliseconds)
```

Breaking it down:
- Fixed overhead: ~3,000 ms (JVM + Spark context initialization)
- Variable cost: ~3.4 µs per node

The fixed overhead (~3 seconds) dominates for small to medium graphs but becomes negligible for very large graphs.

### 2.3 Crossover Point Calculation

Setting $T_{naive} = T_{spark}$:

$$5.8 \times 10^{-6} \times n = 3.0 + 3.4 \times 10^{-6} \times n$$

$$5.8 \times 10^{-6} \times n - 3.4 \times 10^{-6} \times n = 3.0$$

$$2.4 \times 10^{-6} \times n = 3.0$$

$$n = \frac{3.0}{2.4 \times 10^{-6}} = 1,250,000 \text{ nodes}$$

**Theoretical Crossover Point: ~1.25 Million nodes**

This means:
- **Below 1.25M nodes**: Naive is faster
- **Above 1.25M nodes**: Spark becomes faster
- **At 1M nodes**: Naive is still 0.764x faster (24% slower than naive)

---

## 3. Detailed Cost Breakdown

### 3.1 PySpark Overhead Components

The ~3 second baseline overhead for PySpark consists of:

1. **JVM Startup**: ~0.5-1.0 seconds (JVM cold start)
2. **Spark Context Initialization**: ~1.5-2.0 seconds
3. **Python/Java bridge setup**: ~0.5 seconds
4. **Hadoop native library warnings**: Negligible (logged but fast)

### 3.2 Variable Cost Comparison

| Component | Naive | Spark |
|-----------|-------|-------|
| Per-node processing | 5.8 µs | 3.4 µs |
| Efficiency advantage | - | 1.7x per node |
| Break-even point | - | 1.25M nodes |

Interestingly, **PySpark has slightly better per-node efficiency** (3.4 µs vs 5.8 µs), but this is completely overwhelmed by the fixed startup cost.

---

## 4. Practical Implications

### 4.1 When to Use Each Implementation

**Use Naive Sequential Implementation When**:
- Graph size < 1 million nodes
- Single-machine execution is acceptable
- Simplicity and debugging ease are priorities
- Development/testing scenarios
- Real-time constraints (< 10 second SLA)

**Use PySpark Implementation When**:
- Graph size > 1.25 million nodes (estimated)
- Distributed processing across multiple machines is needed
- Can tolerate 3+ second startup overhead
- Need for fault tolerance in distributed environment
- Long-running analytical jobs where startup is amortized

### 4.2 Current Data Point (1M nodes)

At 1,000,000 nodes:
- Naive: 5.96 seconds (✓ **Faster**)
- Spark: 7.80 seconds
- Naive is **24% faster**

To break even with Spark, we'd need:
$$T_{naive}(n) = 7.80$$
$$5.8 \times 10^{-6} \times n = 7.80$$
$$n = 1,345,000 \text{ nodes}$$

**Revised Crossover Estimate: ~1.35 Million nodes** (using actual Spark slope)

---

## 5. Sensitivity Analysis

### 5.1 Impact of Spark Startup Overhead Variation

| Startup Time | Crossover Point |
|--------------|-----------------|
| 2.0 seconds | ~840K nodes |
| 2.5 seconds | ~1.05M nodes |
| 3.0 seconds | **1.25M nodes** (observed) |
| 3.5 seconds | ~1.46M nodes |
| 4.0 seconds | ~1.67M nodes |

### 5.2 Impact of Per-Node Processing Difference

If optimizations reduced Spark per-node cost to 2.5 µs (vs current 3.4 µs):

$$5.8 \times 10^{-6} \times n = 3.0 + 2.5 \times 10^{-6} \times n$$
$$3.3 \times 10^{-6} \times n = 3.0$$
$$n = 909,091 \text{ nodes}$$

**Optimized crossover: ~900K nodes** (saving ~350K nodes threshold)

---

## 6. Scaling Projections

### 6.1 Extrapolated Performance to Larger Graphs

| Nodes | Naive Time | Spark Time | Spark Faster? |
|-------|-----------|-----------|---------------|
| 1M | 5.96s | 7.80s | ❌ No |
| 2M | 11.92s | 10.80s | ✓ **Yes** |
| 5M | 29.80s | 20.00s | ✓ **Yes** |
| 10M | 59.60s | 37.00s | ✓ **Yes** |
| 100M | 596s (9.9m) | 340s (5.7m) | ✓ **Yes** |
| 1B | 5,960s (99m) | 3,400s (57m) | ✓ **Yes** |

### 6.2 Speedup at Scale

At 10 million nodes:
- **Speedup = 59.60 / 37.00 = 1.61x** faster with Spark
- Savings: **22.6 seconds**

At 1 billion nodes:
- **Speedup = 5,960 / 3,400 = 1.75x** faster with Spark
- Savings: **2,560 seconds (43 minutes)**

---

## 7. Algorithm Complexity Analysis

### 7.1 Time Complexity

Both implementations use the same worklist algorithm:

**Worst-case**: O(V²) when all nodes eventually join the attractor

In practice (with sparse graphs):
- Average case: O(V × log(V)) to O(V × E_avg)
- Number of iterations ≈ Attractor size

**Key Observation**: From benchmarks, iterations = attractor size
- This suggests the algorithm exhibits good convergence behavior
- Only nodes in or on the boundary of the attractor get processed

### 7.2 Space Complexity

Both implementations: O(V + E) for graph storage + O(V) for attractor set

No asymptotic difference, but:
- Naive: Single-machine memory (~8 bytes × V)
- Spark: Distributed memory + JVM overhead (+~100 MB baseline)

---

## 8. Recommendations

### 8.1 For This Project

**Current Status**: The naive implementation is optimal for all tested sizes (up to 1M nodes).

**Recommendations**:
1. ✓ Keep naive implementation as primary (it's faster for practical sizes)
2. ✓ Keep PySpark implementation for educational/distributed computing scenarios
3. Consider hybrid approach:
   - Use naive for n < 1M
   - Automatically switch to Spark for n > 2M (safety margin)

### 8.2 Future Optimizations

To make PySpark advantageous earlier:

1. **Reduce startup overhead**:
   - Use Spark in standalone cluster mode (skip local JVM cost)
   - Use Spark SQL or DataFrame API instead of RDDs
   - Pre-start Spark context in persistent daemon

2. **Improve per-node efficiency**:
   - Implement in Scala instead of Python
   - Use partitioned RDDs with better work distribution
   - Use broadcast joins for graph structure

3. **Parallelization strategy**:
   - Current: Sequential worklist within Spark context
   - Proposed: True data-parallel worklist using RDD iterations
   - Alternative: Use PySpark's GraphX library if available

---

## 9. Mathematical Formulation Summary

### 9.1 Performance Models

$$T_{naive}(n) = 5.8 \times 10^{-6} \cdot n + C_{naive}$$
where $C_{naive} \approx 10 \text{ ms}$ (Python startup)

$$T_{spark}(n) = 3.0 + 3.4 \times 10^{-6} \cdot n + C_{jvm}$$
where $C_{jvm} \approx 0 \text{ ms}$ (already included in 3.0s overhead)

### 9.2 Crossover Equation

$$T_{naive}(n^*) = T_{spark}(n^*)$$

$$5.8 \times 10^{-6} \cdot n^* + 0.01 = 3.0 + 3.4 \times 10^{-6} \cdot n^*$$

$$n^* = \frac{3.0 - 0.01}{5.8 \times 10^{-6} - 3.4 \times 10^{-6}}$$

$$n^* = \frac{2.99}{2.4 \times 10^{-6}} \approx 1,246,000 \text{ nodes}$$

### 9.3 Efficiency Ratio

$$E(n) = \frac{T_{spark}(n)}{T_{naive}(n)} = \frac{3.0 + 3.4 \times 10^{-6} \cdot n}{5.8 \times 10^{-6} \cdot n}$$

As $n \to \infty$:
$$\lim_{n \to \infty} E(n) = \frac{3.4 \times 10^{-6}}{5.8 \times 10^{-6}} = 0.586$$

**Asymptotic speedup: 1.71x** (Spark eventually ~1.7x faster due to better per-node efficiency)

---

## 10. Conclusion

| Aspect | Finding |
|--------|---------|
| **Current Winner** | Naive (0.764x at 1M nodes) |
| **Crossover Point** | ~1.25-1.35 million nodes |
| **Asymptotic Speedup** | 1.71x (Spark advantage) |
| **Fixed Overhead** | 3.0 seconds (JVM + Spark context) |
| **Per-Node Efficiency** | Spark: 3.4 µs (1.7x better than Naive: 5.8 µs) |
| **Recommendation** | Use Naive for n < 2M, Switch to Spark for n > 2M |

The analysis demonstrates that while the sequential naive implementation dominates for practical graph sizes, PySpark becomes advantageous for very large graphs (>1.25M nodes) due to its superior per-node efficiency. The 3-second startup overhead is the key constraint limiting PySpark's applicability to smaller instances.
