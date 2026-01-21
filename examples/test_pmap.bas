' Test program for PMAP function
' Tests coordinate mapping between physical and logical coordinates

CLS
PRINT "Testing PMAP Function"
PRINT "====================="
PRINT

' Test 1: Without WINDOW (logical = physical)
PRINT "Test 1: PMAP without WINDOW"
result0 = PMAP(100, 0)
result1 = PMAP(100, 1)
result2 = PMAP(100, 2)
result3 = PMAP(100, 3)
PRINT "  PMAP(100, 0) = "; result0; " (expected: 100)"
PRINT "  PMAP(100, 1) = "; result1; " (expected: 100)"
PRINT "  PMAP(100, 2) = "; result2; " (expected: 100)"
PRINT "  PMAP(100, 3) = "; result3; " (expected: 100)"
PRINT

' Test 2: With WINDOW - logical to physical
PRINT "Test 2: PMAP with WINDOW (0,0)-(100,100)"
SCREEN 13
WINDOW (0, 0)-(100, 100)

' Function 0: Logical X to Physical X
' Logical 0 -> Physical 0, Logical 100 -> Physical 319 (SCREEN 13)
physX0 = PMAP(0, 0)
physX50 = PMAP(50, 0)
physX100 = PMAP(100, 0)
PRINT "  Logical X to Physical X:"
PRINT "    PMAP(0, 0) = "; physX0
PRINT "    PMAP(50, 0) = "; physX50
PRINT "    PMAP(100, 0) = "; physX100
PRINT

' Function 1: Logical Y to Physical Y
' In regular WINDOW, Y increases upward (Cartesian)
physY0 = PMAP(0, 1)
physY50 = PMAP(50, 1)
physY100 = PMAP(100, 1)
PRINT "  Logical Y to Physical Y:"
PRINT "    PMAP(0, 1) = "; physY0
PRINT "    PMAP(50, 1) = "; physY50
PRINT "    PMAP(100, 1) = "; physY100
PRINT

' Test 3: Physical to Logical (reverse mapping)
PRINT "Test 3: Physical to Logical (reverse)"
' Function 2: Physical X to Logical X
logX = PMAP(160, 2)
PRINT "  PMAP(160, 2) = "; logX; " (physical 160 -> logical X)"

' Function 3: Physical Y to Logical Y
logY = PMAP(100, 3)
PRINT "  PMAP(100, 3) = "; logY; " (physical 100 -> logical Y)"
PRINT

' Test 4: Roundtrip conversion
PRINT "Test 4: Roundtrip conversion"
originalX = 25
physX = PMAP(originalX, 0)
backX = PMAP(physX, 2)
PRINT "  Original X: "; originalX
PRINT "  Physical X: "; physX
PRINT "  Back to logical: "; backX
PRINT

originalY = 75
physY = PMAP(originalY, 1)
backY = PMAP(physY, 3)
PRINT "  Original Y: "; originalY
PRINT "  Physical Y: "; physY
PRINT "  Back to logical: "; backY
PRINT

PRINT "PMAP function tests completed!"
END
