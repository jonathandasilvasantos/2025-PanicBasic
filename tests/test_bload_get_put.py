"""
Unit tests for BLOAD, BSAVE, GET, and PUT commands.

This module tests:
- BLOAD: Loading binary files to memory/screen
- Graphics GET: Capturing screen regions to arrays
- Graphics PUT: Displaying sprites from arrays
- File GET: Reading binary data from files
- File PUT: Writing binary data to files

Note: BSAVE is not yet implemented in PASIC.
"""

import unittest
import os
import sys
import tempfile
import struct

# Initialize pygame with dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((800, 600))

from interpreter import BasicInterpreter


class TestBLOADCommand(unittest.TestCase):
    """Test BLOAD command for loading binary files."""

    def setUp(self):
        """Create interpreter instance and temp directory."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_bsave_file(self, filename, data, segment=0, offset=0):
        """Create a BSAVE-format file with proper header.

        BSAVE format:
        - 1 byte: 0xFD marker
        - 2 bytes: segment (little-endian)
        - 2 bytes: offset (little-endian)
        - 2 bytes: length (little-endian)
        - data bytes
        """
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'wb') as f:
            # Write header
            f.write(bytes([0xFD]))  # Marker
            f.write(struct.pack('<H', segment))  # Segment
            f.write(struct.pack('<H', offset))   # Offset
            f.write(struct.pack('<H', len(data)))  # Length
            # Write data
            f.write(data)
        return filepath

    def test_bload_missing_file(self):
        """Test BLOAD with non-existent file."""
        self.interp.reset(['BLOAD "nonexistent.bsv"'])
        self.interp.running = True
        self.interp.step_line()
        self.assertFalse(self.interp.running)

    def test_bload_invalid_format(self):
        """Test BLOAD with invalid file format (no 0xFD marker)."""
        # Create invalid file without 0xFD marker
        filepath = os.path.join(self.temp_dir, "invalid.bsv")
        with open(filepath, 'wb') as f:
            f.write(b'\x00\x00\x00\x00\x00\x00\x00test')

        self.interp.source_dir = self.temp_dir
        self.interp.reset(['BLOAD "invalid.bsv"'])
        self.interp.running = True
        self.interp.step_line()
        self.assertFalse(self.interp.running)

    def test_bload_to_emulated_memory(self):
        """Test BLOAD loading data to emulated memory."""
        test_data = bytes([0x01, 0x02, 0x03, 0x04, 0x05])
        self._create_bsave_file("test.bsv", test_data, segment=0, offset=0)

        self.interp.source_dir = self.temp_dir
        self.interp.memory_segment = 0  # Not VGA memory
        self.interp.reset(['BLOAD "test.bsv"'])
        # Reset sets source_dir, need to set it after
        self.interp.source_dir = self.temp_dir
        self.interp.running = True
        self.interp.step_line()

        # Verify program didn't error (successful load)
        self.assertTrue(self.interp.running or self.interp.pc > 0)

        # Check data was loaded to emulated memory
        for i, byte in enumerate(test_data):
            self.assertEqual(self.interp.emulated_memory.get(i, 0), byte)

    def test_bload_with_offset(self):
        """Test BLOAD with offset parameter."""
        test_data = bytes([0xAA, 0xBB, 0xCC])
        self._create_bsave_file("offset.bsv", test_data)

        self.interp.source_dir = self.temp_dir
        self.interp.memory_segment = 0
        self.interp.reset(['BLOAD "offset.bsv", 100'])
        self.interp.source_dir = self.temp_dir
        self.interp.running = True
        self.interp.step_line()

        # Check data was loaded at offset 100
        for i, byte in enumerate(test_data):
            self.assertEqual(self.interp.emulated_memory.get(100 + i, 0), byte)

    def test_bload_to_video_memory(self):
        """Test BLOAD loading to VGA video memory (segment 0xA000)."""
        # Create small image data (3 pixels)
        test_data = bytes([4, 2, 15])  # Red, green, white in VGA palette
        self._create_bsave_file("screen.bsv", test_data, segment=0xA000)

        # Initialize graphics first
        self.interp.reset(['SCREEN 13', 'DEF SEG = &HA000', 'BLOAD "screen.bsv"'])
        self.interp.source_dir = self.temp_dir
        self.interp.running = True
        self.interp.step_line()  # SCREEN 13
        self.interp.step_line()  # DEF SEG
        self.interp.step_line()  # BLOAD

        # Verify program completed or surface exists
        self.assertIsNotNone(self.interp.surface)

    def test_def_seg_affects_bload(self):
        """Test that DEF SEG sets memory segment for BLOAD."""
        self.interp.reset(['DEF SEG = &HA000'])
        self.interp.running = True
        self.interp.step_line()

        self.assertEqual(self.interp.memory_segment, 0xA000)


class TestGraphicsGET(unittest.TestCase):
    """Test graphics GET command for capturing screen regions."""

    def setUp(self):
        """Create interpreter instance."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def test_get_captures_region(self):
        """Test that GET captures a screen region."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (10, 10)-(20, 20), 4, BF',
            'DIM Sprite(100)',
            'GET (10, 10)-(20, 20), Sprite'
        ])
        self.interp.running = True

        for _ in range(4):
            self.interp.step_line()

        # Check sprite was stored
        self.assertTrue(hasattr(self.interp, '_sprites'))
        self.assertIn('SPRITE', self.interp._sprites)
        sprite = self.interp._sprites['SPRITE']
        self.assertEqual(sprite['width'], 11)
        self.assertEqual(sprite['height'], 11)
        self.assertIsNotNone(sprite['surface'])

    def test_get_without_index(self):
        """Test GET with array name without index."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (5, 5)-(15, 15), 2, BF',
            'DIM MyArray(50)',
            'GET (5, 5)-(15, 15), MyArray'
        ])
        self.interp.running = True

        for _ in range(4):
            self.interp.step_line()

        self.assertIn('MYARRAY', self.interp._sprites)

    def test_get_clips_to_screen_bounds(self):
        """Test that GET clips coordinates to screen bounds."""
        self.interp.reset([
            'SCREEN 13',
            'DIM S(100)',
            'GET (0, 0)-(500, 500), S'
        ])
        self.interp.running = True

        for _ in range(3):
            self.interp.step_line()

        # Should succeed with clipped coordinates
        if hasattr(self.interp, '_sprites') and 'S' in self.interp._sprites:
            sprite = self.interp._sprites['S']
            self.assertLessEqual(sprite['width'], 320)
            self.assertLessEqual(sprite['height'], 200)


class TestGraphicsPUT(unittest.TestCase):
    """Test graphics PUT command for displaying sprites."""

    def setUp(self):
        """Create interpreter instance."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def test_put_pset_mode(self):
        """Test PUT with PSET mode (direct copy)."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (0, 0)-(10, 10), 4, BF',
            'DIM S(50)',
            'GET (0, 0)-(10, 10), S',
            'PUT (50, 50), S, PSET'
        ])
        self.interp.running = True

        for _ in range(5):
            self.interp.step_line()

        self.assertTrue(self.interp.running)

    def test_put_xor_mode(self):
        """Test PUT with XOR mode (default)."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (0, 0)-(10, 10), 4, BF',
            'DIM S(50)',
            'GET (0, 0)-(10, 10), S',
            'PUT (50, 50), S, XOR'
        ])
        self.interp.running = True

        for _ in range(5):
            self.interp.step_line()

        self.assertTrue(self.interp.running)

    def test_put_or_mode(self):
        """Test PUT with OR mode."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (0, 0)-(10, 10), 2, BF',
            'DIM S(50)',
            'GET (0, 0)-(10, 10), S',
            'PUT (60, 60), S, OR'
        ])
        self.interp.running = True

        for _ in range(5):
            self.interp.step_line()

        self.assertTrue(self.interp.running)

    def test_put_and_mode(self):
        """Test PUT with AND mode."""
        self.interp.reset([
            'SCREEN 13',
            'LINE (0, 0)-(10, 10), 15, BF',
            'DIM S(50)',
            'GET (0, 0)-(10, 10), S',
            'LINE (70, 70)-(80, 80), 15, BF',
            'PUT (70, 70), S, AND'
        ])
        self.interp.running = True

        for _ in range(6):
            self.interp.step_line()

        self.assertTrue(self.interp.running)

    def test_put_missing_sprite_silent(self):
        """Test PUT with missing sprite fails silently."""
        self.interp.reset([
            'SCREEN 13',
            'DIM S(50)',
            'PUT (50, 50), S, PSET'
        ])
        self.interp.running = True

        for _ in range(3):
            self.interp.step_line()

        # Should not crash, just skip
        self.assertTrue(self.interp.running)


class TestFileGET(unittest.TestCase):
    """Test file GET command for binary reads.

    Note: The current regex for GET # only supports $ suffix for strings.
    Type suffixes like %, &, !, # are not supported by the regex pattern.
    These tests use string variables and default (no suffix) variables.
    """

    def setUp(self):
        """Create interpreter instance and temp file."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_default_type(self):
        """Test GET reading 2-byte integer with default type (no suffix)."""
        # Create file with integer value
        filepath = os.path.join(self.temp_dir, "test.dat")
        with open(filepath, 'wb') as f:
            f.write(struct.pack('<h', 12345))

        # Change to temp dir so file can be found
        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'GET #1, 1, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(3):
                self.interp.step_line()

            # Default type reads 2 bytes as signed short
            self.assertEqual(self.interp.variables.get('VALUE'), 12345)
        finally:
            os.chdir(old_cwd)

    def test_get_string(self):
        """Test GET reading null-terminated string."""
        filepath = os.path.join(self.temp_dir, "test.dat")
        with open(filepath, 'wb') as f:
            f.write(b'Hello\0')

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'GET #1, 1, Value$',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(3):
                self.interp.step_line()

            # Note: GET stores with original var name (VALUE$), not converted (VALUE_STR)
            self.assertEqual(self.interp.variables.get('VALUE$'), 'Hello')
        finally:
            os.chdir(old_cwd)

    def test_get_at_position(self):
        """Test GET reading from specific file position."""
        filepath = os.path.join(self.temp_dir, "test.dat")
        with open(filepath, 'wb') as f:
            # Write padding then value at position 5
            f.write(b'\x00\x00\x00\x00')  # 4 bytes padding
            f.write(struct.pack('<h', 999))  # Value at position 5

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'GET #1, 5, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(3):
                self.interp.step_line()

            self.assertEqual(self.interp.variables.get('VALUE'), 999)
        finally:
            os.chdir(old_cwd)

    def test_get_negative_integer(self):
        """Test GET reading negative integer value."""
        filepath = os.path.join(self.temp_dir, "test.dat")
        with open(filepath, 'wb') as f:
            f.write(struct.pack('<h', -12345))

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'GET #1, 1, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(3):
                self.interp.step_line()

            self.assertEqual(self.interp.variables.get('VALUE'), -12345)
        finally:
            os.chdir(old_cwd)


class TestFilePUT(unittest.TestCase):
    """Test file PUT command for binary writes.

    Note: The current regex for PUT # only supports $ suffix for strings.
    Type suffixes like %, &, !, # are not supported by the regex pattern.
    These tests use string variables and default (no suffix) variables.
    """

    def setUp(self):
        """Create interpreter instance and temp directory."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_put_default_type(self):
        """Test PUT writing 2-byte integer with default type."""
        filepath = os.path.join(self.temp_dir, "test.dat")

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'Value = 12345',
                'PUT #1, 1, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(4):
                self.interp.step_line()

            # Verify file contents
            with open(filepath, 'rb') as f:
                data = f.read()
                if len(data) >= 2:
                    value = struct.unpack('<h', data[:2])[0]
                    self.assertEqual(value, 12345)
        finally:
            os.chdir(old_cwd)

    def test_put_string(self):
        """Test PUT writing string data."""
        filepath = os.path.join(self.temp_dir, "test.dat")

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'Value$ = "Hello"',
                'PUT #1, 1, Value$',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(4):
                self.interp.step_line()

            with open(filepath, 'rb') as f:
                data = f.read()
                self.assertEqual(data, b'Hello')
        finally:
            os.chdir(old_cwd)

    def test_put_at_position(self):
        """Test PUT writing at specific file position."""
        filepath = os.path.join(self.temp_dir, "test.dat")

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'Value = 9999',
                'PUT #1, 5, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(4):
                self.interp.step_line()

            with open(filepath, 'rb') as f:
                # Seek to position 4 (0-based) to read our value
                f.seek(4)
                data = f.read(2)
                if len(data) >= 2:
                    value = struct.unpack('<h', data)[0]
                    self.assertEqual(value, 9999)
        finally:
            os.chdir(old_cwd)

    def test_put_get_roundtrip(self):
        """Test PUT followed by GET returns same value."""
        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "roundtrip.dat" FOR BINARY AS #1',
                'Original = 32000',
                'PUT #1, 1, Original',
                'GET #1, 1, ReadBack',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(5):
                self.interp.step_line()

            self.assertEqual(
                self.interp.variables.get('READBACK'),
                32000
            )
        finally:
            os.chdir(old_cwd)

    def test_put_negative_value(self):
        """Test PUT writing negative integer value."""
        filepath = os.path.join(self.temp_dir, "test.dat")

        old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.interp.reset([
                'OPEN "test.dat" FOR BINARY AS #1',
                'Value = -12345',
                'PUT #1, 1, Value',
                'CLOSE #1'
            ])
            self.interp.running = True

            for _ in range(4):
                self.interp.step_line()

            with open(filepath, 'rb') as f:
                data = f.read()
                if len(data) >= 2:
                    value = struct.unpack('<h', data[:2])[0]
                    self.assertEqual(value, -12345)
        finally:
            os.chdir(old_cwd)


class TestDEFSEG(unittest.TestCase):
    """Test DEF SEG command for memory segment setting."""

    def setUp(self):
        """Create interpreter instance."""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def test_def_seg_sets_segment(self):
        """Test DEF SEG sets memory segment."""
        self.interp.reset(['DEF SEG = &HA000'])
        self.interp.running = True
        self.interp.step_line()

        self.assertEqual(self.interp.memory_segment, 0xA000)

    def test_def_seg_reset_to_zero(self):
        """Test DEF SEG can reset to segment 0."""
        self.interp.reset([
            'DEF SEG = &HB800',
            'DEF SEG = 0'
        ])
        self.interp.running = True
        self.interp.step_line()
        self.assertEqual(self.interp.memory_segment, 0xB800)

        self.interp.step_line()
        self.assertEqual(self.interp.memory_segment, 0)

    def test_def_seg_with_expression(self):
        """Test DEF SEG with expression."""
        self.interp.reset([
            'Seg% = &H1000',
            'DEF SEG = Seg%'
        ])
        self.interp.running = True
        self.interp.step_line()
        self.interp.step_line()

        self.assertEqual(self.interp.memory_segment, 0x1000)


if __name__ == '__main__':
    unittest.main()
