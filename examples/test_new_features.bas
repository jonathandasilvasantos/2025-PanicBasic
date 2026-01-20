' Test new features
CLS
PRINT "Testing new features..."

' Test TRON/TROFF
PRINT
PRINT "=== TRON/TROFF Test ==="
TRON
PRINT "Trace ON"
TROFF
PRINT "Trace OFF"

' Test VARPTR, VARSEG, SADD
PRINT
PRINT "=== Memory Functions Test ==="
x = 100
addr = VARPTR(x)
seg = VARSEG(x)
PRINT "VARPTR(x) ="; addr
PRINT "VARSEG(x) ="; seg
s$ = "Hello World"
saddr = SADD(s$)
PRINT "SADD(s$) ="; saddr

' Test KEY definitions
PRINT
PRINT "=== KEY Functions Test ==="
KEY 1, "HELP"
PRINT "KEY 1 defined as HELP"
KEY(1) ON
KEY(1) OFF
PRINT "KEY(1) ON/OFF works"

' Test PLAY function
PRINT
PRINT "=== PLAY Function Test ==="
notes = PLAY(0)
PRINT "PLAY(0) ="; notes

' Test $DYNAMIC/$STATIC
'$DYNAMIC
DIM arr(10)
arr(1) = 42
PRINT
PRINT "=== $DYNAMIC Test ==="
PRINT "Array created after $DYNAMIC"
PRINT "arr(1) ="; arr(1)

' Test ON KEY GOSUB handler setup
ON KEY(1) GOSUB keyhandler
PRINT "ON KEY(1) GOSUB handler set"

PRINT
PRINT "All tests completed!"
END

keyhandler:
PRINT "Key handler called"
RETURN
