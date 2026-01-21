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
BOTTLENECK #3: Graphics PUT with Palette Indices
================================================================================
Location: commands/graphics.py:447-459
Impact: Pixel-by-pixel surface rebuild on EVERY PUT call

PROBLEM ANALYSIS:
- When sprite has palette indices, PUT rebuilds surface pixel-by-pixel
- For 16x16 sprite: 256 iterations + 256 set_at() calls per PUT
- No caching of rendered surfaces when palette hasn't changed
- XOR mode also creates temp surfaces and uses surfarray

SUGGESTED FIXES:
[ ] 1. Cache pre-rendered sprite surfaces
     - Add cache dict: sprite_key -> (palette_version, rendered_surface)
     - Track palette version number (increment on PALETTE change)
     - Only rebuild if palette changed since last render

     Example structure:
     self._sprite_render_cache = {
         sprite_key: {
             'palette_version': int,
             'surface': pygame.Surface
         }
     }

[ ] 2. Use numpy for bulk pixel operations
     - HAS_NUMPY is checked but not used for graphics
     - Convert indices array to RGB using numpy vectorization:
       rgb_array = palette_lut[indices_array]
       pygame.surfarray.blit_array(surface, rgb_array)
     - Could be 10-100x faster than per-pixel set_at()

[ ] 3. Pre-compute palette lookup tables
     - Create numpy array: palette_lut[256] = RGB values
     - Allows vectorized index->RGB conversion

[ ] 4. Optimize XOR mode
     - Current: subsurface copy -> surfarray -> XOR -> blit
     - Consider: pygame special blend flags if possible
     - Or: Use numpy for in-place XOR without copy

ESTIMATED IMPROVEMENT: 10-50x faster for sprite-heavy games

================================================================================
BOTTLENECK #4: Statement Parsing Overhead
================================================================================
Location: interpreter.py:3331-3530
Impact: Repeated string operations and regex matching

PROBLEM ANALYSIS:
- statement.upper() called on every statement (line 3336)
- Multiple regex matches per statement in _execute_single_statement
- _extract_first_keyword uses re.match without statement-level caching
- Many command handlers do fullmatch(statement.upper()) again

SUGGESTED FIXES:
[ ] 1. Cache parsed statements
     - For each unique statement, cache: {keyword, parsed_args}
     - Game loops repeat same statements millions of times

[ ] 2. Optimize keyword extraction
     - Instead of regex, use simple string slicing:
       keyword = statement.split()[0].upper()
     - Or use statement[:10].split() to limit scan

[ ] 3. Single uppercase per statement
     - Pass up_stmt to handlers instead of re-uppercasing
     - Currently line 3336 does up_stmt = statement.upper()
     - But handlers also call statement.upper()

[ ] 4. Precompile statement patterns
     - Recognize common patterns like "X = Y" assignments
     - Fast-path frequent statement types

ESTIMATED IMPROVEMENT: 2-5x faster statement dispatch

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

[ ] 9. Reduce dict.items() calls - 29.9M calls
     - Called from eval_expr locals rebuild
     - Part of the eval_locals optimization above

[ ] 10. Optimize frozenset creation in fingerprint
      Line 3131-3136 creates frozensets every eval
      - Cache fingerprint components separately
      - Only rebuild changed parts

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
PROFILING COMMANDS USED
================================================================================
python profile_both.py  # Created during analysis

Key metrics from WETSPOT.BAS (3000 steps):
- Total time: 274.55s
- Steps/sec: 10.9
- eval_expr calls: 5,980,999
- _basic_to_python_identifier calls: 580,086,639
- dict.get calls: 583,489,105
- str.upper calls: 601,089,097

Key metrics from iron_slug.bas (3000 steps):
- Total time: 1.76s
- Steps/sec: 1704.5
- Most time in PLAY audio (time.sleep)
- Demonstrates interpreter CAN be fast with less variable churn
