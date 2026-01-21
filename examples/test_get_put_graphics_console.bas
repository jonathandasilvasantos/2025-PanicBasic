' Test Graphics GET and PUT commands - Console output version
' GET (x1,y1)-(x2,y2), array - captures screen region to array
' PUT (x,y), array, mode - displays sprite with optional mode

SCREEN 13
CLS

LPRINT "Testing Graphics GET and PUT commands..."

' Test 1: Draw a simple shape and capture it with GET
LPRINT "Test 1: Drawing and capturing a shape with GET"
LINE (10, 50)-(30, 70), 4, BF
DIM Sprite(100)
GET (10, 50)-(30, 70), Sprite
LPRINT "Shape captured with GET - PASS"

' Test 2: PUT with PSET mode (direct copy)
LPRINT "Test 2: PUT with PSET mode"
PUT (50, 50), Sprite, PSET
LPRINT "PUT PSET completed - PASS"

' Test 3: PUT with OR mode
LPRINT "Test 3: PUT with OR mode"
PUT (90, 50), Sprite, OR
LPRINT "PUT OR completed - PASS"

' Test 4: PUT with AND mode
LPRINT "Test 4: PUT with AND mode"
LINE (130, 50)-(150, 70), 15, BF
PUT (130, 50), Sprite, AND
LPRINT "PUT AND completed - PASS"

' Test 5: Multiple sprites
LPRINT "Test 5: Multiple sprites"
CIRCLE (180, 60), 10, 2
PAINT (180, 60), 2, 2
DIM Sprite2(100)
GET (170, 50)-(190, 70), Sprite2
LPRINT "Second sprite captured - PASS"

PUT (210, 50), Sprite2, PSET
LPRINT "Second sprite displayed - PASS"

LPRINT ""
LPRINT "All Graphics GET/PUT tests completed!"
END
