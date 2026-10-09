"""
:Core Decoding: White-Box AES for NPVT
:Useful Repos: https://github.com/FrontierTM/Pantegnos
"""
import base64


class NPVTDecrypter:
    def __init__(self, tables_dict):
        self.TY = tables_dict["tyBoxes"]["data"]
        self.MBL = tables_dict["mbl"]["data"]
        self.XT = tables_dict["xorTable"]["data"]
        self.TBL = tables_dict["tboxesLast"]["data"]
        self.SHIFT_ORDER = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

    def _core(self, block):
        buf = list(block)
        buf = [buf[self.SHIFT_ORDER[i]] for i in range(16)]

        for i11 in range(4):
            i13 = i11 * 4
            i14, i15, i16 = i13 + 1, i13 + 2, i13 + 3

            iC = self.TY[i13 * 256 + buf[i13]]
            iC2 = self.TY[i14 * 256 + buf[i14]]
            iC3 = self.TY[i15 * 256 + buf[i15]]
            iC4 = self.TY[i16 * 256 + buf[i16]]

            for i17 in range(4):
                i18 = (i11 * 24) + (i17 * 6)
                i19 = i17 * 8
                i20 = 28 - i19
                i22 = 24 - i19

                n1 = (iC >> i20) & 15
                n2 = (iC2 >> i20) & 15
                n3 = (iC3 >> i20) & 15
                n4 = (iC4 >> i20) & 15
                b10 = self.XT[(i18 * 16 + n1) * 16 + n2]
                b11 = self.XT[(i18 * 16 + n3) * 16 + n4]

                m1 = (iC >> i22) & 15
                m2 = (iC2 >> i22) & 15
                m3 = (iC3 >> i22) & 15
                m4 = (iC4 >> i22) & 15
                lo = self.XT[(i18 + 5) * 256 + self.XT[(i18 + 2) * 256 + m1 * 16 + m2] * 16
                             + self.XT[(i18 + 3) * 256 + m3 * 16 + m4]]
                hi = self.XT[(i18 + 4) * 256 + b10 * 16 + b11]

                buf[i13 + i17] = lo | (hi << 4)

            iC5 = self.MBL[i13 * 256 + buf[i13]]
            iC6 = self.MBL[i14 * 256 + buf[i14]]
            iC7 = self.MBL[i15 * 256 + buf[i15]]
            iC8 = self.MBL[i16 * 256 + buf[i16]]

            for i27 in range(4):
                i28 = (i11 * 24) + (i27 * 6)
                i29 = i27 * 8
                i30 = 28 - i29
                i31 = 24 - i29

                n1 = (iC5 >> i30) & 15
                n2 = (iC6 >> i30) & 15
                n3 = (iC7 >> i30) & 15
                n4 = (iC8 >> i30) & 15
                a1 = self.XT[(i28 * 16 + n1) * 16 + n2]
                a2 = self.XT[(i28 * 16 + n3) * 16 + n4]
                hi = self.XT[(i28 + 4) * 256 + a1 * 16 + a2]

                m1 = (iC5 >> i31) & 15
                m2 = (iC6 >> i31) & 15
                m3 = (iC7 >> i31) & 15
                m4 = (iC8 >> i31) & 15
                b1 = self.XT[(i28 + 2) * 256 + m1 * 16 + m2]
                b2 = self.XT[(i28 + 3) * 256 + m3 * 16 + m4]
                lo = self.XT[(i28 + 5) * 256 + b1 * 16 + b2]

                buf[i13 + i27] = (hi << 4) | lo

        buf = [buf[self.SHIFT_ORDER[i]] for i in range(16)]
        return bytes(self.TBL[i * 256 + buf[i]] for i in range(16))

    def _ctr(self, nonce, data):
        counter = list(nonce)
        out = bytearray(len(data))
        for off in range(0, len(data), 16):
            ks = self._core(counter)
            for i in range(15, -1, -1):
                counter[i] = (counter[i] + 1) & 0xFF
                if counter[i]:
                    break
            block = data[off:off + 16]
            for i, b in enumerate(block):
                out[off + i] = b ^ ks[i]
        return bytes(out)

    def decrypt_text(self, raw_text):
        """Decode the seprated tokens with NPVT1/NPVTSUB1

        :return: raw bytes
        :rtype: list
        """
        out = []
        tokens = raw_text.replace("NPVTSUB1", ",").replace("NPVT1", ",").split(",")
        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue
            try:
                s = "".join(tok.split())
                s += "=" * ((-len(s)) % 4)
                blob = base64.b64decode(s)
            except (ValueError, TypeError):
                continue

            if len(blob) < 32:
                continue

            pt = self._ctr(blob[:16], blob[16:])
            if pt:
                out.append(pt)
        return out
