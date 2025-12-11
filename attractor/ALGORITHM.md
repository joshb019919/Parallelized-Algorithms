# The Attractor Algorithm

Algorithm 1: Attractor of Player 1 to U in a two-player game.

Require: Directed game graph, $G=(V,E)$ with partition $V=(V_1\uplus V_2$; target set $W\subseteq U$).

Ensure: $A\subseteq V$, the winning region of Player 1 to reach W.

1. $A\leftarrow W$ (current attractor approximation)
2. **repeat**
3. $changed\leftarrow false$
4. **for all** $v\in V_1 \setminus A$ **do**      (Player 1 positions)
5. $if \exists (v,w) \in E:w\in A$ **then**
6. $A\leftarrow A\cup \{v\}$
7. $changed\leftarrow true$
8. **end if**
9. **end for**
10. **for all** $v\in V_2 \setminus A$ **do**  (Player 2 positions)
11. Succ($v$) $\leftarrow \{w\in V | (v,w) \in E\}$
12. if Succ($v$) $\subseteq A$ **then**  (all moves lead to the previous attractor)
13. $A\leftarrow A\cup \{v\}$
14. $changed\leftarrow true$
15. **end if**
16. **end for**
17. **until** $changes\leftarrow false$
18. **return** $A$
