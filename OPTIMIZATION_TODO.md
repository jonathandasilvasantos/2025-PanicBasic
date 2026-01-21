================================================================================
PASIC INTERPRETER PERFORMANCE OPTIMIZATION TODO
================================================================================
Profiled: WETSPOT.BAS (10.9 steps/sec) and iron_slug.bas (1704.5 steps/sec)
Date: 2026-01-21

================================================================================
COMPLETED: CRITICAL BOTTLENECK #1 + #2 (Combined Fix)
================================================================================
Status: DONE - Achieved 3.2x speedup (10.9 -> 34.4 steps/sec)

Fix implemented: Pre-compute Python identifier names
- Added _var_py_names, _const_py_names, _func_py_names caches
- On fingerprint change: rebuild name mappings once, store in cache
- On fingerprint match (hot path): use pre-computed names directly
- Eliminates ~574M _basic_to_python_identifier() calls per 3000 steps

Files changed:
- interpreter.py: Added cache dicts to __init__, modified eval_expr(),
  updated reset() to clear caches
- tests/test_eval_optimization.py: New tests for optimization

================================================================================
COMPLETED: BOTTLENECK #3 - Sprite Render Caching
================================================================================
Status: DONE - Caching implemented (38 sprites cached in WETSPOT)

Fix implemented: Cache pre-rendered sprite surfaces with palette version
- Added _palette_version counter (increments on PALETTE changes)
- Added _sprite_render_cache: sprite_key -> (palette_version, surface)
- Added _render_sprite_surface helper method
- Only re-render sprite if palette changed since last render
- Cleared on reset()

Files changed:
- interpreter.py: Added _palette_version and _sprite_render_cache to __init__,
  updated reset() to clear cache, increment version on PALETTE
- commands/graphics.py: Added _render_sprite_surface helper, modified PUT

Note: Benefits vary by game. WETSPOT changes palette 515 times during startup,
causing many cache misses. Games with stable palettes will see larger gains.

Remaining sprite optimizations (lower priority):
[ ] Use numpy for bulk pixel operations in _render_sprite_surface
[ ] Pre-compute palette lookup tables
[ ] Optimize XOR mode

================================================================================
COMPLETED: Fingerprint Optimization
================================================================================
Status: DONE - 16% improvement (34.4 -> 39.9 steps/sec), total 3.7x speedup

Fix implemented: Use count-based fingerprint instead of frozensets
- Changed fingerprint from frozensets of keys to tuple of counts
- Added _proc_func_count to track FUNCTION procedure count
- Avoids creating frozensets on every eval_expr call (was 24M dict.items)

Files changed:
- interpreter.py: Changed fingerprint computation, added _proc_func_count tracking

================================================================================
COMPLETED: Statement Parsing Caching
================================================================================
Status: DONE - 10% improvement (39.9 -> 43.8 steps/sec), total 4.0x speedup

Fix implemented: Cache statement parsing results
- Added _split_cache: line_content -> list of statements
- Added _single_line_if_cache: line_content -> bool
- Caches populated during execution, cleared on reset()
- 914 split cache entries, 1003 IF cache entries in WETSPOT

Files changed:
- interpreter.py: Added caches to __init__, updated _split_statements,
  _is_single_line_if, and reset()
- tests/test_eval_optimization.py: Added TestStatementCaching tests

Remaining statement parsing opportunities (diminishing returns):
[ ] Optimize keyword extraction (string split vs regex)
[ ] Pass up_stmt to handlers to avoid re-uppercasing

================================================================================
BOTTLENECK #5: convert_basic_expr() Regex Overhead
================================================================================
Location: interpreter.py:778-861
Impact: Multiple regex substitutions per expression

PROBLEM ANALYSIS:
- Expression cache helps (4s cumtime vs 80s for eval_expr)
- But uncached expressions do 15+ regex substitutions
- While loop at line 824 for integer division is inefficient
- Identifier regex at line 855 scans full expression

SUGGESTED FIXES:
[ ] 1. Single-pass expression tokenizer
     - Instead of multiple regex.sub() passes
     - Tokenize once, transform tokens, rejoin
     - More maintainable and potentially faster

[ ] 2. Pre-tokenize on program load
     - Parse expressions during program loading
     - Store AST or token list instead of string

[ ] 3. Simple expression fast-path
     - For expressions like "X" or "X + 1" or "X > 0"
     - Skip full conversion machinery

ESTIMATED IMPROVEMENT: 2-3x faster for uncached expressions

================================================================================
BOTTLENECK #6: GET Graphics Pixel-by-Pixel Capture
================================================================================
Location: commands/graphics.py:361-367
Impact: Nested loop for capturing palette indices

PROBLEM ANALYSIS:
- When capturing sprite with palette indices:
  for py in range(height):
      for px in range(width):
          indices[py * width + px] = self._pixel_indices[src_idx]
- For 16x16 sprite: 256 Python loop iterations

SUGGESTED FIXES:
[ ] 1. Use numpy array slicing
     - If _pixel_indices is numpy array:
       indices = self._pixel_indices[y1:y2+1, x1:x2+1].flatten()
     - Single operation instead of nested loop

[ ] 2. Use memoryview for bytearray operations
     - Faster than Python loop for byte copying

ESTIMATED IMPROVEMENT: 5-20x faster sprite capture

================================================================================
MEDIUM PRIORITY IMPROVEMENTS
================================================================================

[ ] 7. Optimize _split_statements() - Line 7294
     Impact: 5s cumtime, 6M calls
     - Character-by-character loop for colon splitting
     - Consider: str.split(':') with string quote awareness
     - Or: regex-based split respecting quotes

[ ] 8. Optimize _is_single_line_if() - Line 7239
     Impact: 2.6s cumtime, 6M calls
     - Character loop to find THEN position
     - Cache result keyed by statement hash

[x] 9. Reduce dict.items() calls - DONE
     - Fixed as part of identifier caching optimization
     - dict.items() calls reduced from 24M to ~6M per 3000 steps

[x] 10. Optimize frozenset creation in fingerprint - DONE
      - Changed fingerprint to use counts instead of frozensets
      - Eliminates all frozenset creation overhead

================================================================================
ARCHITECTURAL SUGGESTIONS
================================================================================

[ ] 11. Consider bytecode compilation
     - Parse program once into bytecode
     - Execute bytecode instead of parsing strings
     - Eliminates regex and string operations on hot path
     - Major rewrite but could be 50-100x faster

[ ] 12. JIT compilation for hot loops
     - Detect frequently executed code paths
     - Generate optimized Python/Cython code
     - Complex but high payoff for game loops

[ ] 13. Use __slots__ for interpreter state
     - Reduces memory and improves attribute access
     - Minor improvement but easy to implement

[ ] 14. Consider PyPy compatibility
     - JIT compilation could give 5-10x speedup
     - Would need to avoid pygame C extensions

================================================================================
QBASIC SIMILARITY RECOMMENDATIONS
================================================================================
Your intuition about being more like QBASIC is correct:

[ ] 15. Pre-parse program structure
     - QBASIC compiles to intermediate representation
     - Know label positions, variable types at load time
     - Current: Discovers labels/types during execution

[ ] 16. Type-aware variable storage
     - QBASIC knows X% is integer at compile time
     - Store typed arrays directly, not generic dicts
     - Faster access and less conversion

[ ] 17. Static array allocation
     - QBASIC allocates arrays at DIM time
     - Pre-compute array bounds and storage
     - Currently re-validates on each access

================================================================================
IMPLEMENTATION PRIORITY ORDER
================================================================================
1. Fix #1 + #2 (identifier caching) - Highest impact, moderate effort
2. Fix #3 (sprite caching) - High impact for games, moderate effort
3. Fix #4 (statement caching) - Medium impact, low effort
4. Fix #6 (GET numpy) - High impact, low effort if numpy available
5. Fix #5 (tokenizer) - Medium impact, higher effort
6. Consider #11 (bytecode) for long-term 50x improvement

================================================================================
PROFILING RESULTS - BEFORE AND AFTER OPTIMIZATION
================================================================================

BEFORE (baseline):
  WETSPOT.BAS (3000 steps):
  - Total time: 274.55s
  - Steps/sec: 10.9
  - _basic_to_python_identifier calls: 580,086,639
  - str.upper calls: 601,089,097
  - dict.items calls: 24,000,000+

AFTER (all optimizations applied):
  WETSPOT.BAS (3000 steps):
  - Total time: 68.45s
  - Steps/sec: 43.8
  - **SPEEDUP: 4.0x**
  - str.upper calls: 21,000,000 (96% reduction)
  - dict.items calls: ~6,000,000 (75% reduction)
  - _basic_to_python_identifier calls: 5,244 (99.999% reduction!)
  - Statement split cache: 914 entries (avoids repeated parsing)
  - Single-line IF cache: 1003 entries (avoids repeated checks)

iron_slug.bas (3000 steps):
- Total time: 1.76s
- Steps/sec: 1704.5 (unchanged - most time in PLAY audio)
- Demonstrates interpreter can be fast with less variable churn

================================================================================
OPTIMIZATIONS COMPLETED
================================================================================
1. Pre-computed Python identifier names (3.2x speedup)
2. Sprite render caching with palette versioning
3. Count-based fingerprint (avoids frozenset creation)

These optimizations are low-risk, well-tested, and provide meaningful speedup
for real BASIC programs like WETSPOT.BAS.
