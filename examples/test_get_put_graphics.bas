' Test Graphics GET and PUT commands
' GET (x1,y1)-(x2,y2), array - captures screen region to array
' PUT (x,y), array, mode - displays sprite with optional mode

SCREEN 13
CLS

PRINT "Testing Graphics GET and PUT commands..."

' Test 1: Draw a simple shape and capture it with GET
PRINT "Test 1: Drawing and capturing a shape with GET"

' Draw a red square
LINE (10, 50)-(30, 70), 4, BF

' Capture the square into sprite array
DIM Sprite%(100)
GET (10, 50)-(30, 70), Sprite%
PRINT "PASS: Shape captured with GET"

' Test 2: PUT with PSET mode (direct copy)
PRINT "Test 2: PUT with PSET mode"
PUT (50, 50), Sprite%, PSET
PRINT "PASS: PUT PSET completed"

' Test 3: PUT with XOR mode (default)
PRINT "Test 3: PUT with XOR mode"
PUT (90, 50), Sprite%, XOR
PRINT "PASS: PUT XOR completed"

' Test 4: PUT with OR mode
PRINT "Test 4: PUT with OR mode"
PUT (130, 50), Sprite%, OR
PRINT "PASS: PUT OR completed"

' Test 5: PUT with AND mode
PRINT "Test 5: PUT with AND mode"
' First draw a white background
LINE (170, 50)-(190, 70), 15, BF
PUT (170, 50), Sprite%, AND
PRINT "PASS: PUT AND completed"

' Test 6: Multiple sprites with array indexing
PRINT "Test 6: Multiple sprites with indexing"

' Draw a green circle
CIRCLE (220, 60), 10, 2
PAINT (220, 60), 2, 2

' Capture as second sprite
DIM Sprite2%(100)
GET (210, 50)-(230, 70), Sprite2%
PRINT "PASS: Second sprite captured"

' Display second sprite
PUT (250, 50), Sprite2%, PSET
PRINT "PASS: Second sprite displayed"

' Test 7: XOR animation simulation (draw and erase)
PRINT "Test 7: XOR mode animation (draw/erase)"
FOR I = 1 TO 3
    PUT (50, 100), Sprite%, XOR
    ' Brief delay
    FOR J = 1 TO 1000: NEXT J
    PUT (50, 100), Sprite%, XOR
NEXT I
PRINT "PASS: XOR animation completed"

PRINT ""
PRINT "All Graphics GET/PUT tests completed!"
PRINT "Press any key to exit..."

' Wait for keypress
WaitKey:
K$ = INKEY$
IF K$ = "" THEN GOTO WaitKey
END
