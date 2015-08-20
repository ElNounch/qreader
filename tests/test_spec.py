from unittest import TestCase
from qreader.constants import MODE_SIZE_SMALL, MODE_SIZE_MEDIUM, MODE_SIZE_LARGE, MODE_KANJI, MODE_ALPHA_NUM, \
    MODE_NUMBER, MODE_BYTES
from qreader.spec import get_mask_func, mode_sizes_for_version, bits_for_length, get_dead_zones

__author__ = 'ewino'


class TestMasks(TestCase):
    def test_mask_bounds(self):
        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            for i in range(177):
                for j in range(177):
                    self.assertIn(mask_func(i, j), (0, 1))

    def test_nonexistent_masks(self):
        self.assertRaises(TypeError, lambda: get_mask_func(-1))
        self.assertRaises(TypeError, lambda: get_mask_func(8))

    def test_mask_formula_correctness(self):
        mask_samples = {
            0: '1010101010101010101010101010101010101010101010101',
            1: '1111111000000011111110000000111111100000001111111',
            2: '1001001100100110010011001001100100110010011001001',
            3: '1001001001001001001001001001001001001001001001001',
            4: '1110001111000100011100001110111000111100010001110',
            5: '1111111100000110010011010101100100110000011111111',
            6: '1111111111000111011011010101101101110001111111111',
            7: '1010101000111010001110101010111000101110001010101',
        }

        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            mask_result = ''
            for i in range(7):
                for j in range(7):
                    mask_result += '1' if mask_func(i, j) else '0'
            self.assertEqual(mask_samples[mask_id], mask_result)


class TestCharCounts(TestCase):

    def test_size_for_version(self):
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(1))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(2))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(5))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(9))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(10))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(11))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(12))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(20))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(26))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(27))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(28))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(39))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(40))

    def test_size_for_illegal_versions(self):
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(0))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(-1))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(41))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(0.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(-1.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(10.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(9.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(40.5))

    def test_char_counts(self):
        self.assertEqual(8, bits_for_length(8, MODE_KANJI))
        self.assertEqual(9, bits_for_length(8, MODE_ALPHA_NUM))
        self.assertEqual(10, bits_for_length(8, MODE_NUMBER))

        self.assertEqual(10, bits_for_length(18, MODE_KANJI))
        self.assertEqual(11, bits_for_length(18, MODE_ALPHA_NUM))
        self.assertEqual(12, bits_for_length(18, MODE_NUMBER))

        self.assertEqual(12, bits_for_length(28, MODE_KANJI))
        self.assertEqual(13, bits_for_length(28, MODE_ALPHA_NUM))
        self.assertEqual(14, bits_for_length(28, MODE_NUMBER))

        self.assertEqual(8, bits_for_length(8, MODE_BYTES))
        self.assertEqual(16, bits_for_length(18, MODE_BYTES))
        self.assertEqual(16, bits_for_length(28, MODE_BYTES))

    def test_illegal_char_counts(self):
        # illegal version
        self.assertRaises(ValueError, lambda: bits_for_length(0, 1))
        self.assertRaises(ValueError, lambda: bits_for_length(41, 1))
        self.assertRaises(ValueError, lambda: bits_for_length(8.5, 1))

        # illegal modes
        self.assertRaises(TypeError, lambda: bits_for_length(8, 0))
        self.assertRaises(TypeError, lambda: bits_for_length(8, -1))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 3))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 7))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 9))


class TestDeadZones(TestCase):
    REGULAR_ZONES_COUNT = 6

    def test_normal_dead_zones(self):
        self.assertEqual(self.REGULAR_ZONES_COUNT, len(get_dead_zones(1)))

    def test_alignment_patterns_amount(self):
        amounts = sum(([p**2] * x for p, x in enumerate([1, 5, 7, 7, 7, 7, 6])), [])  # 1*0, 5*1, 7*9, 7*16, 7*25...
        self.assertEqual(40, len(amounts))
        for version, amount in enumerate(amounts, start=1):
            self.assertEqual(amount, len(get_dead_zones(version)) - self.REGULAR_ZONES_COUNT)

    def test_illegal_versions(self):
        self.assertRaises(ValueError, lambda: get_dead_zones(-1))
        self.assertRaises(ValueError, lambda: get_dead_zones(0))
        self.assertRaises(ValueError, lambda: get_dead_zones(1.5))
        self.assertRaises(ValueError, lambda: get_dead_zones(41))