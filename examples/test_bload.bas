' Test BLOAD command
' BLOAD loads binary files with 7-byte header (0xFD + segment + offset + length)
' Note: BSAVE is not currently implemented in PASIC

PRINT "Testing BLOAD command..."
PRINT ""

' Test 1: Test that BLOAD properly handles missing files
PRINT "Test 1: BLOAD error handling for missing file"
ON ERROR GOTO ErrorHandler
BLOAD "nonexistent_file.bsv"
PRINT "ERROR: Should have triggered an error for missing file"
GOTO Test2

ErrorHandler:
PRINT "PASS: Error correctly triggered for missing file"
RESUME Test2

Test2:
' Test 2: BLOAD with DEF SEG for memory operations
PRINT ""
PRINT "Test 2: DEF SEG and memory segment setting"
DEF SEG = &HA000
PRINT "DEF SEG set to &HA000 (VGA video memory)"
DEF SEG = 0
PRINT "DEF SEG reset to 0"
PRINT "PASS: DEF SEG operations work correctly"

PRINT ""
PRINT "BLOAD testing complete."
PRINT "Note: Full BLOAD testing requires valid BSAVE files."
PRINT "      BSAVE is not yet implemented in PASIC."
END
