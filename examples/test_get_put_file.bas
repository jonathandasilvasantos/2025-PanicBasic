' Test File GET and PUT commands (binary file I/O)
' GET #filenum, recordnum, variable - reads binary data from file
' PUT #filenum, recordnum, variable - writes binary data to file
'
' Note: The current implementation supports:
' - Default type variables (2-byte integer): Value, TestInt, etc.
' - String variables ($): Value$, TestString$
' Type suffixes %, &, !, # are NOT supported in GET/PUT regex

PRINT "Testing File GET and PUT commands..."
PRINT ""

' Test 1: PUT and GET with default type (integer) variables
PRINT "Test 1: PUT and GET integer values (default type)"
OPEN "test_binary.dat" FOR BINARY AS #1

' Write some integers
TestInt = 12345
PUT #1, 1, TestInt
TestInt = -9876
PUT #1, 3, TestInt
TestInt = 32767
PUT #1, 5, TestInt

' Read them back
GET #1, 1, ReadInt
PRINT "Read value 1: "; ReadInt;
IF ReadInt = 12345 THEN PRINT " PASS" ELSE PRINT " FAIL"

GET #1, 3, ReadInt
PRINT "Read value 2: "; ReadInt;
IF ReadInt = -9876 THEN PRINT " PASS" ELSE PRINT " FAIL"

GET #1, 5, ReadInt
PRINT "Read value 3: "; ReadInt;
IF ReadInt = 32767 THEN PRINT " PASS" ELSE PRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"
PRINT ""

' Test 2: PUT and GET with strings
PRINT "Test 2: PUT and GET string values"
OPEN "test_binary.dat" FOR BINARY AS #1

TestString$ = "Hello"
PUT #1, 1, TestString$

GET #1, 1, ReadString$
PRINT "Read string: '"; ReadString$; "'";
IF ReadString$ = "Hello" THEN PRINT " PASS" ELSE PRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"
PRINT ""

' Test 3: PUT at specific position
PRINT "Test 3: PUT and GET at specific positions"
OPEN "test_binary.dat" FOR BINARY AS #1

Value1 = 111
Value2 = 222
Value3 = 333

' Write at specific positions
PUT #1, 1, Value1
PUT #1, 5, Value2
PUT #1, 9, Value3

' Read back from same positions
GET #1, 1, Read1
GET #1, 5, Read2
GET #1, 9, Read3

PRINT "Position 1: "; Read1;
IF Read1 = 111 THEN PRINT " PASS" ELSE PRINT " FAIL"
PRINT "Position 5: "; Read2;
IF Read2 = 222 THEN PRINT " PASS" ELSE PRINT " FAIL"
PRINT "Position 9: "; Read3;
IF Read3 = 333 THEN PRINT " PASS" ELSE PRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"
PRINT ""

' Test 4: Negative values
PRINT "Test 4: PUT and GET negative values"
OPEN "test_binary.dat" FOR BINARY AS #1

NegVal = -32000
PUT #1, 1, NegVal

GET #1, 1, ReadNeg
PRINT "Negative value: "; ReadNeg;
IF ReadNeg = -32000 THEN PRINT " PASS" ELSE PRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"
PRINT ""

' Test 5: Roundtrip test
PRINT "Test 5: Roundtrip PUT then GET"
OPEN "test_binary.dat" FOR BINARY AS #1

Original = 12321
PUT #1, 1, Original
GET #1, 1, Returned

PRINT "Original: "; Original; " Returned: "; Returned;
IF Original = Returned THEN PRINT " PASS" ELSE PRINT " FAIL"

CLOSE #1
KILL "test_binary.dat"

PRINT ""
PRINT "All File GET/PUT tests completed!"
END
