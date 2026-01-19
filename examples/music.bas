' ============================================
' MUSIC.BAS - Sound Generation Demo
' Demonstrates BEEP and SOUND commands
' ============================================

SCREEN 13
RANDOMIZE TIMER

' Color constants
CONST BLACK = 0
CONST BLUE = 1
CONST GREEN = 2
CONST CYAN = 3
CONST RED = 4
CONST MAGENTA = 5
CONST YELLOW = 14
CONST WHITE = 15

' Note frequencies (Hz) for one octave
DIM noteFreq(12)
noteFreq(0) = 262   ' C4
noteFreq(1) = 277   ' C#4
noteFreq(2) = 294   ' D4
noteFreq(3) = 311   ' D#4
noteFreq(4) = 330   ' E4
noteFreq(5) = 349   ' F4
noteFreq(6) = 370   ' F#4
noteFreq(7) = 392   ' G4
noteFreq(8) = 415   ' G#4
noteFreq(9) = 440   ' A4
noteFreq(10) = 466  ' A#4
noteFreq(11) = 494  ' B4

' Note names for display
DIM noteName$(12)
noteName$(0) = "C "
noteName$(1) = "C#"
noteName$(2) = "D "
noteName$(3) = "D#"
noteName$(4) = "E "
noteName$(5) = "F "
noteName$(6) = "F#"
noteName$(7) = "G "
noteName$(8) = "G#"
noteName$(9) = "A "
noteName$(10) = "A#"
noteName$(11) = "B "

' Main menu
mainMenu:
CLS
COLOR WHITE
LOCATE 2, 10
PRINT "SOUND GENERATION DEMO"
LOCATE 3, 10
PRINT "===================="

COLOR CYAN
LOCATE 6, 5
PRINT "1. Play Scale (C Major)"
LOCATE 7, 5
PRINT "2. Play Chromatic Scale"
LOCATE 8, 5
PRINT "3. Play Simple Melody"
LOCATE 9, 5
PRINT "4. Sound Effects Demo"
LOCATE 10, 5
PRINT "5. Piano Keyboard Mode"
LOCATE 11, 5
PRINT "6. Frequency Sweep"
LOCATE 13, 5
PRINT "Q. Quit"

COLOR YELLOW
LOCATE 16, 5
PRINT "Press a key to select..."

' Wait for key
waitKey:
k$ = INKEY$
IF k$ = "" THEN GOTO waitKey

IF k$ = "1" THEN GOTO playScale
IF k$ = "2" THEN GOTO playChromaticScale
IF k$ = "3" THEN GOTO playMelody
IF k$ = "4" THEN GOTO soundEffects
IF k$ = "5" THEN GOTO pianoMode
IF k$ = "6" THEN GOTO freqSweep
IF k$ = "q" OR k$ = "Q" THEN GOTO exitProgram
IF k$ = CHR$(27) THEN GOTO exitProgram
GOTO waitKey

' ============================================
' Play C Major Scale
' ============================================
playScale:
CLS
COLOR WHITE
LOCATE 2, 10
PRINT "C MAJOR SCALE"
LOCATE 3, 10
PRINT "============="

' C major scale: C D E F G A B C
DIM scaleNotes(8)
scaleNotes(0) = 0   ' C
scaleNotes(1) = 2   ' D
scaleNotes(2) = 4   ' E
scaleNotes(3) = 5   ' F
scaleNotes(4) = 7   ' G
scaleNotes(5) = 9   ' A
scaleNotes(6) = 11  ' B
scaleNotes(7) = 12  ' C (next octave)

FOR i = 0 TO 7
    noteIdx = scaleNotes(i)
    IF noteIdx < 12 THEN
        freq = noteFreq(noteIdx)
        name$ = noteName$(noteIdx)
    ELSE
        ' Next octave C
        freq = noteFreq(0) * 2
        name$ = "C "
    END IF

    ' Draw note indicator
    GOSUB drawNoteBar

    ' Play the note
    SOUND freq, 6
    _DELAY 0.4
NEXT i

COLOR GREEN
LOCATE 20, 5
PRINT "Press any key to continue..."
GOSUB waitAnyKey
GOTO mainMenu

' ============================================
' Play Chromatic Scale
' ============================================
playChromaticScale:
CLS
COLOR WHITE
LOCATE 2, 8
PRINT "CHROMATIC SCALE"
LOCATE 3, 8
PRINT "==============="

FOR i = 0 TO 11
    freq = noteFreq(i)
    name$ = noteName$(i)

    GOSUB drawNoteBar

    SOUND freq, 4
    _DELAY 0.25
NEXT i

' Go back down
FOR i = 11 TO 0 STEP -1
    freq = noteFreq(i)
    name$ = noteName$(i)

    GOSUB drawNoteBar

    SOUND freq, 4
    _DELAY 0.25
NEXT i

COLOR GREEN
LOCATE 20, 5
PRINT "Press any key to continue..."
GOSUB waitAnyKey
GOTO mainMenu

' ============================================
' Play Simple Melody (Twinkle Twinkle)
' ============================================
playMelody:
CLS
COLOR WHITE
LOCATE 2, 6
PRINT "SIMPLE MELODY"
LOCATE 3, 6
PRINT "============="
COLOR CYAN
LOCATE 5, 3
PRINT "(Twinkle Twinkle Little Star)"

' Melody notes (as indices into noteFreq)
' C C G G A A G, F F E E D D C
DIM melody(14)
DIM melodyLen(14)
melody(0) = 0: melodyLen(0) = 6   ' C
melody(1) = 0: melodyLen(1) = 6   ' C
melody(2) = 7: melodyLen(2) = 6   ' G
melody(3) = 7: melodyLen(3) = 6   ' G
melody(4) = 9: melodyLen(4) = 6   ' A
melody(5) = 9: melodyLen(5) = 6   ' A
melody(6) = 7: melodyLen(6) = 12  ' G (longer)
melody(7) = 5: melodyLen(7) = 6   ' F
melody(8) = 5: melodyLen(8) = 6   ' F
melody(9) = 4: melodyLen(9) = 6   ' E
melody(10) = 4: melodyLen(10) = 6 ' E
melody(11) = 2: melodyLen(11) = 6 ' D
melody(12) = 2: melodyLen(12) = 6 ' D
melody(13) = 0: melodyLen(13) = 12' C (longer)

FOR i = 0 TO 13
    noteIdx = melody(i)
    freq = noteFreq(noteIdx)
    dur = melodyLen(i)
    name$ = noteName$(noteIdx)

    GOSUB drawNoteBar

    SOUND freq, dur
    _DELAY dur / 18.2 + 0.05
NEXT i

COLOR GREEN
LOCATE 20, 5
PRINT "Press any key to continue..."
GOSUB waitAnyKey
GOTO mainMenu

' ============================================
' Sound Effects Demo
' ============================================
soundEffects:
CLS
COLOR WHITE
LOCATE 2, 8
PRINT "SOUND EFFECTS DEMO"
LOCATE 3, 8
PRINT "=================="

' Laser sound
COLOR CYAN
LOCATE 6, 5
PRINT "1. Laser..."
FOR f = 1000 TO 200 STEP -50
    SOUND f, 1
    _DELAY 0.02
NEXT f
_DELAY 0.5

' Rising tone
LOCATE 8, 5
PRINT "2. Rising tone..."
FOR f = 200 TO 800 STEP 20
    SOUND f, 1
    _DELAY 0.02
NEXT f
_DELAY 0.5

' Alarm
LOCATE 10, 5
PRINT "3. Alarm..."
FOR j = 1 TO 3
    FOR f = 400 TO 800 STEP 100
        SOUND f, 2
        _DELAY 0.08
    NEXT f
    FOR f = 800 TO 400 STEP -100
        SOUND f, 2
        _DELAY 0.08
    NEXT f
NEXT j
_DELAY 0.5

' Explosion
LOCATE 12, 5
PRINT "4. Explosion..."
FOR i = 1 TO 20
    f = INT(RND * 200) + 50
    SOUND f, 1
    _DELAY 0.03
NEXT i
_DELAY 0.5

' Power up
LOCATE 14, 5
PRINT "5. Power up..."
FOR f = 100 TO 1500 STEP 50
    SOUND f, 1
    _DELAY 0.015
NEXT f
_DELAY 0.5

' Beep
LOCATE 16, 5
PRINT "6. Simple BEEP..."
BEEP
_DELAY 0.5

COLOR GREEN
LOCATE 20, 5
PRINT "Press any key to continue..."
GOSUB waitAnyKey
GOTO mainMenu

' ============================================
' Piano Keyboard Mode
' ============================================
pianoMode:
CLS
COLOR WHITE
LOCATE 2, 8
PRINT "PIANO KEYBOARD MODE"
LOCATE 3, 8
PRINT "==================="

COLOR CYAN
LOCATE 5, 3
PRINT "Keys: A S D F G H J K (C to C)"
LOCATE 6, 3
PRINT "      W E   T Y U   (sharps)"
LOCATE 8, 3
PRINT "Press ESC to return to menu"

' Draw piano keyboard
GOSUB drawKeyboard

pianoLoop:
k$ = INKEY$
IF k$ = "" THEN GOTO pianoLoop
IF k$ = CHR$(27) THEN GOTO mainMenu

' Map keys to notes
playNote = -1
IF k$ = "a" OR k$ = "A" THEN playNote = 0   ' C
IF k$ = "w" OR k$ = "W" THEN playNote = 1   ' C#
IF k$ = "s" OR k$ = "S" THEN playNote = 2   ' D
IF k$ = "e" OR k$ = "E" THEN playNote = 3   ' D#
IF k$ = "d" OR k$ = "D" THEN playNote = 4   ' E
IF k$ = "f" OR k$ = "F" THEN playNote = 5   ' F
IF k$ = "t" OR k$ = "T" THEN playNote = 6   ' F#
IF k$ = "g" OR k$ = "G" THEN playNote = 7   ' G
IF k$ = "y" OR k$ = "Y" THEN playNote = 8   ' G#
IF k$ = "h" OR k$ = "H" THEN playNote = 9   ' A
IF k$ = "u" OR k$ = "U" THEN playNote = 10  ' A#
IF k$ = "j" OR k$ = "J" THEN playNote = 11  ' B
IF k$ = "k" OR k$ = "K" THEN playNote = 12  ' C (high)

IF playNote >= 0 THEN
    IF playNote < 12 THEN
        freq = noteFreq(playNote)
        name$ = noteName$(playNote)
    ELSE
        freq = noteFreq(0) * 2
        name$ = "C "
    END IF

    ' Show note being played
    COLOR YELLOW
    LOCATE 18, 15
    PRINT "Playing: "; name$; " ("; freq; " Hz)  "

    ' Highlight key
    GOSUB highlightKey

    SOUND freq, 4
    _DELAY 0.15

    ' Redraw keyboard
    GOSUB drawKeyboard
END IF

GOTO pianoLoop

' ============================================
' Frequency Sweep
' ============================================
freqSweep:
CLS
COLOR WHITE
LOCATE 2, 8
PRINT "FREQUENCY SWEEP"
LOCATE 3, 8
PRINT "==============="

COLOR CYAN
LOCATE 5, 3
PRINT "Sweeping from 100 Hz to 2000 Hz"
LOCATE 7, 3
PRINT "Press any key to stop..."

sweepY = 100
FOR f = 100 TO 2000 STEP 10
    ' Check for key press to stop
    k$ = INKEY$
    IF k$ <> "" THEN GOTO sweepDone

    ' Draw frequency bar
    barLen = (f - 100) / 10
    IF barLen > 300 THEN barLen = 300

    ' Color based on frequency
    IF f < 400 THEN
        barColor = RED
    ELSEIF f < 800 THEN
        barColor = YELLOW
    ELSEIF f < 1200 THEN
        barColor = GREEN
    ELSE
        barColor = CYAN
    END IF

    LINE (10, sweepY)-(10 + barLen, sweepY + 30), barColor, BF

    ' Show frequency
    COLOR WHITE
    LOCATE 10, 5
    PRINT "Frequency: "; f; " Hz    "

    SOUND f, 1
    _DELAY 0.02

    ' Clear bar for next iteration
    LINE (10, sweepY)-(310, sweepY + 30), BLACK, BF
NEXT f

sweepDone:
COLOR GREEN
LOCATE 20, 5
PRINT "Press any key to continue..."
GOSUB waitAnyKey
GOTO mainMenu

' ============================================
' Exit Program
' ============================================
exitProgram:
CLS
COLOR WHITE
LOCATE 10, 10
PRINT "Goodbye!"
BEEP
_DELAY 0.5
END

' ============================================
' Subroutines
' ============================================

drawNoteBar:
    ' Draw a visual bar for the note
    barY = 80
    barHeight = 40

    ' Clear previous bar
    LINE (0, barY)-(319, barY + barHeight + 20), BLACK, BF

    ' Calculate bar width based on frequency
    barWidth = (freq - 200) / 3
    IF barWidth < 20 THEN barWidth = 20
    IF barWidth > 280 THEN barWidth = 280

    ' Color based on note
    noteColor = (noteIdx MOD 7) + 9

    LINE (20, barY)-(20 + barWidth, barY + barHeight), noteColor, BF

    ' Show note name and frequency
    COLOR WHITE
    LOCATE 11, 5
    PRINT "Note: "; name$; "  Freq: "; freq; " Hz    "

    RETURN

drawKeyboard:
    ' Draw simple piano keyboard representation
    keyY = 120
    keyW = 30
    keyH = 60

    ' Draw white keys
    FOR i = 0 TO 7
        LINE (20 + i * keyW, keyY)-(20 + (i + 1) * keyW - 2, keyY + keyH), WHITE, BF
        LINE (20 + i * keyW, keyY)-(20 + (i + 1) * keyW - 2, keyY + keyH), BLACK, B
    NEXT i

    ' Draw black keys (C#, D#, F#, G#, A#)
    ' Positions: after C, D, F, G, A
    blackPos = 0
    FOR i = 0 TO 4
        IF i = 0 THEN blackPos = 0
        IF i = 1 THEN blackPos = 1
        IF i = 2 THEN blackPos = 3
        IF i = 3 THEN blackPos = 4
        IF i = 4 THEN blackPos = 5

        bx = 20 + blackPos * keyW + keyW - 10
        LINE (bx, keyY)-(bx + 20, keyY + 35), BLACK, BF
    NEXT i

    ' Draw key labels
    COLOR BLACK
    LOCATE 15, 4
    PRINT "A S D F G H J K"
    COLOR WHITE
    LOCATE 13, 5
    PRINT "W E   T Y U"

    RETURN

highlightKey:
    ' Highlight the played key
    keyY = 120
    keyW = 30
    keyH = 60

    ' Map note to key position
    IF playNote = 0 THEN kx = 0   ' C
    IF playNote = 2 THEN kx = 1   ' D
    IF playNote = 4 THEN kx = 2   ' E
    IF playNote = 5 THEN kx = 3   ' F
    IF playNote = 7 THEN kx = 4   ' G
    IF playNote = 9 THEN kx = 5   ' A
    IF playNote = 11 THEN kx = 6  ' B
    IF playNote = 12 THEN kx = 7  ' C high

    ' Check if it's a white or black key
    isBlack = 0
    IF playNote = 1 OR playNote = 3 OR playNote = 6 OR playNote = 8 OR playNote = 10 THEN
        isBlack = 1
    END IF

    IF isBlack = 0 THEN
        ' Highlight white key
        LINE (20 + kx * keyW + 2, keyY + 2)-(20 + (kx + 1) * keyW - 4, keyY + keyH - 2), YELLOW, BF
    ELSE
        ' Highlight black key
        IF playNote = 1 THEN bx = 0
        IF playNote = 3 THEN bx = 1
        IF playNote = 6 THEN bx = 3
        IF playNote = 8 THEN bx = 4
        IF playNote = 10 THEN bx = 5

        bxPos = 20 + bx * keyW + keyW - 10
        LINE (bxPos + 2, keyY + 2)-(bxPos + 18, keyY + 33), YELLOW, BF
    END IF

    RETURN

waitAnyKey:
    wk$ = INKEY$
    IF wk$ = "" THEN GOTO waitAnyKey
    RETURN
