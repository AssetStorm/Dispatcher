# -*- coding: utf-8 -*-
import unittest
from hypothesis import given
from hypothesis.strategies import SearchStrategy, integers, from_regex, permutations, lists, one_of


class Enigma:
    def __init__(self, patch_key: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                 rotor_selection: list = [0, 1, 2], reflector_selection: int = 0,
                 r1_pos: int = 0, r2_pos: int = 0, r3_pos: int = 0):
        self.position = 0
        self.pk = patch_key
        self.al = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        rotors = ['EKMFLGDQVZNTOWYHXUSPAIBRCJ',
                  'AJDKSIRUXBLHWTMCQGZNPYFVOE',
                  'BDFHJLCPRTXVZNYEIWGAKMUSQO',
                  'ESOVPZJAYQUIRHXLNFTGKDCMWB',
                  'VZBRGITYUPSDNHLXAWMJQOFECK']
        reflectors = ['EJMZALYXVBWFCRQUONTSPIKHGD',
                      'YRUHQSLDPXNGOKMIEBFZCWVJAT',
                      'FVPJIAOYEDRZXWGCTKUQSBNMHL']
        self.r1 = rotors[rotor_selection[0]]
        self.r2 = rotors[rotor_selection[1]]
        self.r3 = rotors[rotor_selection[2]]
        self.re = reflectors[reflector_selection]
        self.r1p = r1_pos
        self.r2p = r2_pos
        self.r3p = r3_pos
        self.c_offset = int('A'.encode('ascii')[0])

    def reset(self, new_pos: int = 0):
        self.position = new_pos

    def encrypt_char(self, c: str) -> str:
        step0 = self.pk[int(c.encode('ascii')[0]) - self.c_offset]
        step1 = self.r1[(int(step0.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al)**2) + self.r1p) % len(self.al)]
        step2 = self.r2[(int(step1.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al)) + self.r2p) % len(self.al)]
        step3 = self.r3[(int(step2.encode('ascii')[0]) - self.c_offset +
                         self.position + self.r3p) % len(self.al)]
        step4 = self.re[int(step3.encode('ascii')[0]) - self.c_offset]
        step5 = self.r3[(int(step4.encode('ascii')[0]) - self.c_offset +
                         self.position + self.r3p) % len(self.al)]
        step6 = self.r2[(int(step5.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al)) + self.r2p) % len(self.al)]
        step7 = self.r1[(int(step6.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al)**2) + self.r1p) % len(self.al)]
        step8 = self.pk[int(step7.encode('ascii')[0]) - self.c_offset]
        self.position += 1
        return step8

    def decrypt_char(self, c: str) -> str:
        step0 = self.al[self.pk.index(c[0]) % len(self.al)]
        step1 = self.al[(self.r1.index(step0[0]) - (self.position // len(self.al)**2) - self.r1p) % len(self.al)]
        step2 = self.al[(self.r2.index(step1[0]) - (self.position // len(self.al)) - self.r2p) % len(self.al)]
        step3 = self.al[(self.r3.index(step2[0]) - self.position - self.r3p) % len(self.al)]
        step4 = self.al[self.re.index(step3[0]) % len(self.al)]
        step5 = self.al[(self.r3.index(step4[0]) - self.position - self.r3p) % len(self.al)]
        step6 = self.al[(self.r2.index(step5[0]) - (self.position // len(self.al)) - self.r2p) % len(self.al)]
        step7 = self.al[(self.r1.index(step6[0]) - (self.position // len(self.al)**2) - self.r1p) % len(self.al)]
        step8 = self.al[self.pk.index(step7[0]) % len(self.al)]
        self.position += 1
        return step8

    def encrypt(self, plain_text: str, start_pos: int = 0) -> str:
        self.reset(start_pos)
        return "".join([self.encrypt_char(c) for c in plain_text])

    def decrypt(self, cipher_text: str, start_pos: int = 0) -> str:
        self.reset(start_pos)
        return "".join([self.decrypt_char(c) for c in cipher_text])


def radiogram() -> SearchStrategy:
    normal_word = from_regex(r'[A-Z]{1,15}', fullmatch=True)
    name = normal_word.map(lambda w: "X" + w + "X" + w + "X")
    sentence = lists(elements=one_of(normal_word, name), min_size=1, max_size=12).map(lambda x: "".join(x) + "X")
    return lists(sentence, min_size=1, max_size=5).map(lambda s: "".join(s))


class EnigmaTestCase(unittest.TestCase):
    def check_enigma(self, plaintext: str, r1p: int = 0, r2p: int = 0, r3p: int = 0):
        enigma = Enigma(r1_pos=r1p, r2_pos=r2p, r3_pos=r3p)
        cipher_text = enigma.encrypt(plaintext)
        self.assertNotEqual(plaintext, cipher_text)
        self.assertEqual(plaintext, enigma.decrypt(cipher_text))

    def test_hello_world(self):
        self.check_enigma("HELLOWORLD")

    def test_real_example(self):
        plaintext = "DASOBERKOMMANDODERWEHRMAQTGIBTBEKANNTXAACHENXAACHENXISTGERETTETX" + \
                    "DURQGEBUENDELTENEINSATZDERHILFSKRAEFTEKONNTEDIEBEDROHUNGABGEWENDET" + \
                    "UNDDIERETTUNGDERSTADTGEGENXEINSXAQTXNULLXNULLXUHRSIQERGESTELLTWERDENX"
        patch_key = 'DBNATLIHGVZFMCOUYRSEPJXWQK'
        r1p = 16
        r2p = 26
        r3p = 8
        enigma = Enigma(patch_key=patch_key, rotor_selection=[0, 3, 2], reflector_selection=1,
                        r1_pos=r1p, r2_pos=r2p, r3_pos=r3p)
        cipher_text = enigma.encrypt(plaintext)
        self.assertEqual('YTCBORYNCVSQAWDTMVVDMVVCLWSPNPVKLLWUIAVUVDAYUIWUTCZWMTDWUGBQZCJ' +
                         'ZBFJNBYQZVZPPTXDQJQQFMBXXFXPYEROURJPFNCUYDZOZMVGPEYJYKPHDLGKNOB' +
                         'TJGMMMEMVLOIWWOBTZNERYOJOWCDZLVEVVPYPHNSYNCQXKIAGOWVSEWPXPCMXPW' +
                         'APVYFHLYCK', cipher_text)
        self.assertEqual(plaintext, enigma.decrypt(cipher_text))

    @given(integers(min_value=0, max_value=26),
           integers(min_value=0, max_value=26),
           integers(min_value=0, max_value=26),
           from_regex(r'[A-Z]', fullmatch=True))
    def test_same_characters_different_sequence(self, r1p: int, r2p: int, r3p: int, repeated_char: str):
        enigma = Enigma(r1_pos=r1p, r2_pos=r2p, r3_pos=r3p)
        cipher_text = enigma.encrypt(repeated_char[0]*26)
        for test_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.assertNotEqual(cipher_text, test_char*26)
        self.assertEqual(repeated_char[0]*26, enigma.decrypt(cipher_text))

    @given(integers(min_value=0, max_value=26),
           integers(min_value=0, max_value=26),
           integers(min_value=0, max_value=26),
           permutations(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
           permutations(list(range(5))),
           integers(min_value=0, max_value=2),
           radiogram())
    def test_encrypt_decrypt(self, r1p: int, r2p: int, r3p: int, patch_key: str,
                             rotor_selection: list, reflector_selection: int, plaintext: str):
        enigma = Enigma(r1_pos=r1p, r2_pos=r2p, r3_pos=r3p, patch_key=patch_key,
                        rotor_selection=rotor_selection, reflector_selection=reflector_selection)
        cipher_text = enigma.encrypt(plaintext)
        self.assertNotEqual(cipher_text, plaintext)
        self.assertEqual(plaintext, enigma.decrypt(cipher_text))


if __name__ == '__main__':  # pragma: no mutate
    unittest.main()  # pragma: no cover
