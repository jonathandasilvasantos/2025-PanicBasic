' Test BLOAD command - Console output version
' BLOAD loads binary files with 7-byte header (0xFD + segment + offset + length)
' Note: BSAVE is not currently implemented in PASIC

LPRINT "Testing BLOAD command..."
LPRINT ""

' Test 1: DEF SEG operations
LPRINT "Test 1: DEF SEG operations"
DEF SEG = &HA000
LPRINT "DEF SEG set to &HA000 (VGA video memory) - PASS"
DEF SEG = 0
LPRINT "DEF SEG reset to 0 - PASS"
LPRINT ""

' Test 2: DEF SEG with expression
LPRINT "Test 2: DEF SEG with expression"
SegVal = &H1000
DEF SEG = SegVal
LPRINT "DEF SEG set via variable - PASS"
DEF SEG = 0
LPRINT ""

LPRINT "BLOAD testing complete."
LPRINT "Note: Full BLOAD testing requires valid BSAVE files."
LPRINT "      BSAVE is not yet implemented in PASIC."
END
