import unittest

from server.util import translate_to_tex
from server.constants import STRINGS


class TranslatorTest(unittest.TestCase):

    def test_translator(self):

        wrong_format = [("[Verse] I wanna be the very best$",
                         STRINGS.TRANSLATOR.ERROR_STRING_CONTAINS_FORBIDDEN_CHARACTERS),
                        ("[Verse] Like no one ever was!^@",
                         STRINGS.TRANSLATOR.ERROR_STRING_CONTAINS_FORBIDDEN_CHARACTERS),
                        ("[Verse] To catch them is my * real test",
                         STRINGS.TRANSLATOR.ERROR_STRING_CONTAINS_FORBIDDEN_CHARACTERS),
                        ("[Verse] To train <>them is my cause",
                         STRINGS.TRANSLATOR.ERROR_STRING_CONTAINS_FORBIDDEN_CHARACTERS),
                        ("Toto je nas skautsky zpevnik",
                         STRINGS.TRANSLATOR.ERROR_NO_STARTING_BLOCK)]

        correct_format = [
            "[verse]\nThe sky is a [Em]neighborhood, [B] [G] so keep it [A]down\n[C] The heart is a [Em]storybook, [A]a star burned out\nThe sky is a [Em]neighborhood, [B] [G] don't make a [A]sound\n[C] Lights coming [Em]up ahead, [A]don't look now\n\nThe sky is a [Em]neighborhood [B] [G] [A]\nThe sky is a [C]neighborhood, [Em] [A]don't look now\n",
            "[solo]\n[C] [Em] [Bb] [A]\n[G] [Gb] The [F]sky is a neighborhood",
            "[verse]\nStíny [E]dnů a snů se k obratníku [A]stáčí\nRuce [E]snů černejch se snaží zakrýt [A]oči\nSvětlo [F#mi]tvý prozradí proč já [E]vím\nS novým [F#mi]dnem že se [A]zas navrá[H]tí",
            "[Chorus]\n[E]Jenže tenhle zlej mě [A]strejda vyčítá,\n[G]že se mu to taky blbě [B]počítá.\nAle já [Emi]výlevy a provokace\nzavostalý generace [A]nevydejchám, [Ami]nevydejchám."
        ]

        for song in wrong_format:
            _, log = translate_to_tex(song[0])
            assert song[1] == log, "Log mismatch:\nText:\n{}\nExpected:\n{}\nLog:\n{}".format(
                song[0], song[1], log)

        for song in correct_format:
            _, log = translate_to_tex(song)
            assert log == "", "Log found where it shouldn't:\nText:\n{}\nLog:\n{}".format(song, log)
