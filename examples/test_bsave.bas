' Test program for BSAVE statement
' Tests saving memory block to binary file

CLS
PRINT "Testing BSAVE Statement"
PRINT "======================="
PRINT

' Test 1: Save and load emulated memory
PRINT "Test 1: BSAVE/BLOAD with emulated memory"
DEF SEG = &H3000
POKE 0, 65
POKE 1, 66
POKE 2, 67
POKE 3, 68
POKE 4, 69
PRINT "  Original data: ";
FOR i = 0 TO 4
  PRINT CHR$(PEEK(i));
NEXT i
PRINT

BSAVE "test_mem.bin", 0, 5
PRINT "  Saved 5 bytes to test_mem.bin"

' Clear the memory
FOR i = 0 TO 4
  POKE i, 0
NEXT i
PRINT "  Cleared memory"

' Load it back
BLOAD "test_mem.bin", 0
PRINT "  Loaded data back: ";
FOR i = 0 TO 4
  PRINT CHR$(PEEK(i));
NEXT i
PRINT
PRINT

' Test 2: Save with offset
PRINT "Test 2: BSAVE with offset"
DEF SEG = &H4000
FOR i = 0 TO 9
  POKE i, 48 + i  ' ASCII '0' to '9'
NEXT i
PRINT "  Original: ";
FOR i = 0 TO 9
  PRINT CHR$(PEEK(i));
NEXT i
PRINT

' Save bytes 5-9 (offset 5, length 5)
BSAVE "test_offset.bin", 5, 5
PRINT "  Saved offset 5, length 5"

' Clear and reload
FOR i = 0 TO 9
  POKE i, 0
NEXT i
BLOAD "test_offset.bin", 0
PRINT "  Loaded at offset 0: ";
FOR i = 0 TO 4
  PRINT CHR$(PEEK(i));
NEXT i
PRINT
PRINT

' Clean up files
KILL "test_mem.bin"
KILL "test_offset.bin"
PRINT "Cleaned up test files"
PRINT

PRINT "BSAVE tests completed!"
END
