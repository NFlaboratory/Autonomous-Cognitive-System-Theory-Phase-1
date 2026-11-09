# CR-2b の検査：実験で用いた機構の全変種

| 領域（実験） | 変種 | (i-a) | (i-b) | (ii) | (iii) | (iv) | CR-2b |
|---|---|---|---|---|---|---|---|
| MinACS (E7) | D0 | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (E7) | D-en+1 | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (E7) | D-en+2 | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (E7) | D-tp+1 | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (E7) | D-blindcold | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (E7) | D-stalefood | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | full | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -integ | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -feas | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -resp | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -envuse | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -select | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -update | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (E8) | -phys | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (P11) | est-2 | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (P11) | est-2 | ○ | ○ | ○ | ○ | ○ | 成立 |
| MinACS (P11) | est-3 | ○ | ○ | ○ | ○ | ○ | 成立 |
| Furnace (P11) | est-3 | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | full | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -integ | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -feas | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -resp | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -envuse | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -select | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -update | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -phys | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -auto | ○ | ○ | ○ | ○ | ○ | 成立 |
| v2 (E2) | -relation | ○ | ○ | ○ | ○ | ○ | 成立 |

- ○：例を見つけた（その節は成り立つ）。×：探索の範囲で例が見つからなかった。
- MinACS・炉番は X×E_ext の全数と列挙した M で探索した（× はその範囲での不成立）。v2 は固定した格子（4 セル × energy 6 × integ 3 × temp 2、背景 2）での探索で、× は「格子上で見つからない」の意味。
- P11 の upd-k は Update だけを変えるので（CR-2b は Update を含まない）、基準の機構と同じ結果になる。表には est-k だけを載せた。
- 評価写像 P_val には、MinACS・炉番は M2 の出力全体、v2 は M2 の出力の (P, ev, sig, evrq) を用いた。
