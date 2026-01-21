' Test File GET and PUT commands (binary file I/O)
' Console output version using LPRINT

LPRINT "Testing File GET and PUT commands..."
LPRINT ""

' Test 1: PUT and GET with default type (integer) variables
LPRINT "Test 1: PUT and GET integer values"
OPEN "test_binary.dat" FOR BINARY AS #1

TestInt = 12345
PUT #1, 1, TestInt

GET #1, 1, ReadInt
LPRINT "Read value: "; ReadInt;
IF ReadInt = 12345 THEN LPRINT " PASS" ELSE LPRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"

' Test 2: PUT and GET with strings
LPRINT "Test 2: PUT and GET string values"
OPEN "test_binary.dat" FOR BINARY AS #1

TestString$ = "Hello"
PUT #1, 1, TestString$

GET #1, 1, ReadString$
LPRINT "Read string: '"; ReadString$; "'";
IF ReadString$ = "Hello" THEN LPRINT " PASS" ELSE LPRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"

' Test 3: Negative values
LPRINT "Test 3: PUT and GET negative values"
OPEN "test_binary.dat" FOR BINARY AS #1

NegVal = -32000
PUT #1, 1, NegVal

GET #1, 1, ReadNeg
LPRINT "Negative value: "; ReadNeg;
IF ReadNeg = -32000 THEN LPRINT " PASS" ELSE LPRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"

' Test 4: Roundtrip test
LPRINT "Test 4: Roundtrip PUT then GET"
OPEN "test_binary.dat" FOR BINARY AS #1

Original = 12321
PUT #1, 1, Original
GET #1, 1, Returned

LPRINT "Original: "; Original; " Returned: "; Returned;
IF Original = Returned THEN LPRINT " PASS" ELSE LPRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"

LPRINT ""
LPRINT "All File GET/PUT tests completed!"
END
