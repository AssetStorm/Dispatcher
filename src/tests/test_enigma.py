# -*- coding: utf-8 -*-
import unittest


class Enigma:
    def __init__(self):
        self.position = 0
        self.al = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.r1 = 'FIYRKJAQXLUZGNOHVSMEPDWTBC'
        self.r2 = 'NECLKJTGSUMZQAFPBXRHVWDOYI'
        self.r3 = 'IORGKSYZBLHXMJUFQDNPVTAECW'
        self.c_offset = int('A'.encode('ascii')[0])

    def reset(self, new_pos: int = 0):
        self.position = new_pos

    def encrypt_char(self, c: str) -> str:
        step1 = self.r1[(int(c.encode('ascii')[0]) - self.c_offset +
                         self.position) % len(self.al)]
        step2 = self.r2[(int(step1.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al))) % len(self.al)]
        step3 = self.r3[int(step2.encode('ascii')[0]) - self.c_offset]
        step4 = self.r2[(int(step3.encode('ascii')[0]) - self.c_offset +
                         (self.position // len(self.al))) % len(self.al)]
        step5 = self.r1[(int(step4.encode('ascii')[0]) - self.c_offset +
                         self.position) % len(self.al)]
        self.position += 1
        return step5

    def decrypt_char(self, c: str) -> str:
        step1 = self.al[(self.r1.index(c[0]) - self.position) % len(self.al)]
        step2 = self.al[(self.r2.index(step1[0]) - (self.position // len(self.al))) % len(self.al)]
        step3 = self.al[self.r3.index(step2[0]) % len(self.al)]
        step4 = self.al[(self.r2.index(step3[0]) - (self.position // len(self.al))) % len(self.al)]
        step5 = self.al[(self.r1.index(step4[0]) - self.position) % len(self.al)]
        self.position += 1
        return step5

    def encrypt(self, plain_text: str, start_pos: int = 0) -> str:
        self.reset(start_pos)
        return "".join([self.encrypt_char(c) for c in plain_text])

    def decrypt(self, cipher_text: str, start_pos: int = 0) -> str:
        self.reset(start_pos)
        return "".join([self.decrypt_char(c) for c in cipher_text])


class EnigmaTestCase(unittest.TestCase):
    def check_enigma(self, plaintext: str, offset: int = 0):
        enigma = Enigma()
        cipher_text = enigma.encrypt(plaintext, start_pos=offset)
        self.assertNotEqual(plaintext, cipher_text)
        self.assertEqual(plaintext, enigma.decrypt(cipher_text, start_pos=offset))

    def test_hello_world(self):
        self.check_enigma("HELLOWORLD")

    def test_same_characters_different_sequence(self):
        enigma = Enigma()
        cipher_text = enigma.encrypt("AAAAAAA", start_pos=0)
        self.assertNotEqual(cipher_text[0], cipher_text[1])
        self.assertNotEqual(cipher_text[1], cipher_text[2])
        self.assertNotEqual(cipher_text[2], cipher_text[3])
        self.assertNotEqual(cipher_text[3], cipher_text[4])
        self.assertNotEqual(cipher_text[4], cipher_text[5])
        self.assertNotEqual(cipher_text[5], cipher_text[6])
        self.assertNotEqual(cipher_text[6], cipher_text[0])
        self.assertEqual("AAAAAAA", enigma.decrypt(cipher_text, start_pos=0))


if __name__ == '__main__':  # pragma: no mutate
    unittest.main()  # pragma: no cover
