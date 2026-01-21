' Test program for Microsoft Binary Format conversion functions
' Tests CVSMBF, CVDMBF, MKSMBF$, MKDMBF$

CLS
PRINT "Testing Microsoft Binary Format Conversion Functions"
PRINT "===================================================="
PRINT

' Test 1: Zero values
PRINT "Test 1: Zero value roundtrip"
mbfSingle$ = MKSMBF$(0)
mbfDouble$ = MKDMBF$(0)
singleResult = CVSMBF(mbfSingle$)
doubleResult = CVDMBF(mbfDouble$)
PRINT "  MKSMBF$(0) length: "; LEN(mbfSingle$); " (expected: 4)"
PRINT "  MKDMBF$(0) length: "; LEN(mbfDouble$); " (expected: 8)"
PRINT "  CVSMBF roundtrip: "; singleResult; " (expected: 0)"
PRINT "  CVDMBF roundtrip: "; doubleResult; " (expected: 0)"
PRINT

' Test 2: Positive values
PRINT "Test 2: Positive value roundtrip"
originalSingle = 3.14159
originalDouble# = 2.718281828#
mbfSingle$ = MKSMBF$(originalSingle)
mbfDouble$ = MKDMBF$(originalDouble#)
singleResult = CVSMBF(mbfSingle$)
doubleResult# = CVDMBF(mbfDouble$)
PRINT "  Original single: "; originalSingle
PRINT "  CVSMBF result:   "; singleResult
PRINT "  Original double: "; originalDouble#
PRINT "  CVDMBF result:   "; doubleResult#
PRINT

' Test 3: Negative values
PRINT "Test 3: Negative value roundtrip"
originalSingle = -42.5
originalDouble# = -123.456789#
mbfSingle$ = MKSMBF$(originalSingle)
mbfDouble$ = MKDMBF$(originalDouble#)
singleResult = CVSMBF(mbfSingle$)
doubleResult# = CVDMBF(mbfDouble$)
PRINT "  Original single: "; originalSingle
PRINT "  CVSMBF result:   "; singleResult
PRINT "  Original double: "; originalDouble#
PRINT "  CVDMBF result:   "; doubleResult#
PRINT

' Test 4: Value 1.0 (known MBF representation)
PRINT "Test 4: Value 1.0 roundtrip"
mbfSingle$ = MKSMBF$(1.0)
mbfDouble$ = MKDMBF$(1.0)
singleResult = CVSMBF(mbfSingle$)
doubleResult = CVDMBF(mbfDouble$)
PRINT "  MKSMBF$(1.0) -> CVSMBF: "; singleResult; " (expected: 1)"
PRINT "  MKDMBF$(1.0) -> CVDMBF: "; doubleResult; " (expected: 1)"
PRINT

' Test 5: Large values
PRINT "Test 5: Large value roundtrip"
originalSingle = 1234567
originalDouble# = 9876543210.123#
mbfSingle$ = MKSMBF$(originalSingle)
mbfDouble$ = MKDMBF$(originalDouble#)
singleResult = CVSMBF(mbfSingle$)
doubleResult# = CVDMBF(mbfDouble$)
PRINT "  Original single: "; originalSingle
PRINT "  CVSMBF result:   "; singleResult
PRINT "  Original double: "; originalDouble#
PRINT "  CVDMBF result:   "; doubleResult#
PRINT

' Test 6: Small values
PRINT "Test 6: Small value roundtrip"
originalSingle = 0.000123
originalDouble# = 0.000000123456#
mbfSingle$ = MKSMBF$(originalSingle)
mbfDouble$ = MKDMBF$(originalDouble#)
singleResult = CVSMBF(mbfSingle$)
doubleResult# = CVDMBF(mbfDouble$)
PRINT "  Original single: "; originalSingle
PRINT "  CVSMBF result:   "; singleResult
PRINT "  Original double: "; originalDouble#
PRINT "  CVDMBF result:   "; doubleResult#
PRINT

PRINT "All MBF conversion tests completed!"
END
