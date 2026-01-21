' Test program for ERL and ERR functions
' Tests error handling with ERL (error line) and ERR (error code)

CLS
PRINT "Testing ERL and ERR functions"
PRINT "=============================="
PRINT

' Test 1: ERL and ERR without any error
PRINT "Test 1: ERL and ERR without error"
PRINT "  ERL = "; ERL; " (expected: 0)"
PRINT "  ERR = "; ERR; " (expected: 0)"
PRINT

' Set up error handler
ON ERROR GOTO ErrorHandler

' Test 2: Trigger error 5 (Illegal function call)
PRINT "Test 2: Triggering ERROR 5"
testnum = 2
ERROR 5
PRINT "  Resumed after ERROR 5"
PRINT

' Test 3: Trigger error 11 (Division by zero)
PRINT "Test 3: Triggering ERROR 11"
testnum = 3
ERROR 11
PRINT "  Resumed after ERROR 11"
PRINT

' Test 4: Trigger error 53 (File not found)
PRINT "Test 4: Triggering ERROR 53"
testnum = 4
ERROR 53
PRINT "  Resumed after ERROR 53"
PRINT

' Test 5: Use ERL and ERR in an expression
PRINT "Test 5: ERL and ERR in expressions"
testnum = 5
ERROR 7
PRINT "  Resumed after ERROR 7"
PRINT

' Disable error handler for final test
ON ERROR GOTO 0

PRINT "All error handling tests completed successfully!"
PRINT
END

ErrorHandler:
  PRINT "  Error caught in handler:"
  PRINT "    Error Code (ERR): "; ERR
  PRINT "    Error Line (ERL): "; ERL

  ' Test 5 also calculates combined value
  IF testnum = 5 THEN
    combined = ERL * 100 + ERR
    PRINT "    Combined (ERL*100+ERR): "; combined
  END IF

  RESUME NEXT
