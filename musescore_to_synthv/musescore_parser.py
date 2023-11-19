import xml.etree.ElementTree as ET
from .common import txt


class XMLParser:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.set_staff_start_cb = None
        self.set_staff_end_cb = None
        self.set_time_signature_cb = None
        self.set_pitch_cb = None
        self.set_rest_cb = None
        self.set_lyric_cb = None
        self.set_tie_cb = None
        self.set_dot_cb = None
        self.set_tuplet_cb = None
        self.SET_TAB = txt.TAB * 30

    def _print_verbose(self, *args):
        if self.verbose:
            print(*args)

    def set_time_signature(self, n, d):
        self._print_verbose(
            self.SET_TAB + txt.CRED + "set_time_signature" + txt.CEND, n, d
        )
        if self.set_time_signature_cb:
            self.set_time_signature_cb(n, d)

    def parse_time_signature(self, v):
        n = d = ""
        for t in v.findall("./"):
            self._print_verbose(
                txt.TAB * 4,
                txt.CBEIGE + t.tag + txt.CEND,
                [t.attrib, t.tail.strip(), str(t.text).strip()],
            )
            if t.tag == "sigN":
                n = t.text
            elif t.tag == "sigD":
                d = t.text
        self.set_time_signature(n, d)

    def set_pitch(self, pitch, duration):
        self._print_verbose(
            self.SET_TAB + txt.CRED + "set_pitch" + txt.CEND, pitch, duration
        )
        if self.set_pitch_cb:
            self.set_pitch_cb(pitch, duration)

    def set_lyric(self, lyric):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_lyric" + txt.CEND, lyric)
        if self.set_lyric_cb:
            self.set_lyric_cb(lyric)

    def set_tie(self):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_tie" + txt.CEND)
        if self.set_tie_cb:
            self.set_tie_cb()

    def set_dot(self, num):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_dot" + txt.CEND, num)
        if self.set_dot_cb:
            self.set_dot_cb(num)

    def parse_chord(self, v):
        duration = ""
        for c in v.findall("./"):
            self._print_verbose(
                txt.TAB * 4,
                txt.CBEIGE + c.tag + txt.CEND,
                [c.attrib, c.tail.strip(), str(c.text).strip()],
            )
            if c.tag == "durationType":
                duration = c.text
            elif c.tag == "dots":
                self.set_dot(c.text)
            elif c.tag == "Lyrics":
                for l in c.findall("./"):
                    self._print_verbose(
                        txt.TAB * 5,
                        txt.CRED2 + l.tag + txt.CEND,
                        [l.attrib, l.tail.strip(), str(l.text).strip()],
                    )
                    if l.tag == "text" and l.text is not None:
                        self.set_lyric(l.text)
            elif c.tag == "Note":
                for n in c.findall("./"):
                    self._print_verbose(
                        txt.TAB * 5,
                        txt.CRED2 + n.tag + txt.CEND,
                        [n.attrib, n.tail.strip(), str(n.text).strip()],
                    )
                    if n.tag == "Spanner" and n.attrib["type"] == "Tie":
                        for s in n.findall("./"):
                            self._print_verbose(
                                txt.TAB * 6,
                                s.tag,
                                [s.attrib, s.tail.strip(), str(s.text).strip()],
                            )
                            if s.tag == "next":
                                self.set_tie()
                    elif n.tag == "pitch":
                        self.set_pitch(n.text, duration)

    def set_rest(self, duration):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_rest" + txt.CEND, duration)
        if self.set_rest_cb:
            self.set_rest_cb(duration)

    def parse_rest(self, v):
        for r in v.findall("./"):
            self._print_verbose(
                txt.TAB * 4,
                txt.CBEIGE + r.tag + txt.CEND,
                [r.attrib, r.tail.strip(), str(r.text).strip()],
            )
            if r.tag == "durationType":
                self.set_rest(r.text)

    def set_tuplet(self, status):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_tuplet" + txt.CEND, status)
        if self.set_tuplet_cb:
            self.set_tuplet_cb(status)

    def parse_root(self, r):
        for s in r.findall("./Score/Staff"):
            self._print_verbose(
                txt.CBLUE + s.tag + txt.CEND,
                [s.attrib, s.tail.strip(), str(s.text).strip()],
            )
            m_count = 0
            if self.set_staff_start_cb:
                self.set_staff_start_cb()
            for m in s.findall("./"):
                self._print_verbose(
                    txt.TAB * 1,
                    txt.CGREEN + m.tag + txt.CEND,
                    m_count,
                    [m.attrib, m.tail.strip(), str(m.text).strip()],
                )
                if m.tag == "Measure":
                    m_count += 1
                    for w in m.findall("./"):
                        self._print_verbose(
                            txt.TAB * 2,
                            txt.CVIOLET + w.tag + txt.CEND,
                            [w.attrib, w.tail.strip(), str(w.text).strip()],
                        )
                        if w.tag == "voice":
                            for v in w.findall("./"):
                                self._print_verbose(
                                    txt.TAB * 3,
                                    txt.CYELLOW + v.tag + txt.CEND,
                                    [v.attrib, v.tail.strip(), str(v.text).strip()],
                                )
                                if v.tag == "TimeSig":
                                    self.parse_time_signature(v)
                                elif v.tag == "Chord":
                                    self.parse_chord(v)
                                elif v.tag == "Rest":
                                    self.parse_rest(v)
                                elif v.tag == "Tuplet":
                                    self.set_tuplet(True)
                                elif v.tag == "endTuplet":
                                    self.set_tuplet(False)

            if self.set_staff_end_cb:
                self.set_staff_end_cb()

    def parse_xml(
        self,
        xml_file,
        set_staff_start_func=None,
        set_staff_end_func=None,
        set_time_signature_func=None,
        set_pitch_func=None,
        set_rest_func=None,
        set_lyric_func=None,
        set_tie_func=None,
        set_dot_func=None,
        set_tuplet_func=None,
    ):
        self.set_staff_start_cb = set_staff_start_func
        self.set_staff_end_cb = set_staff_end_func
        self.set_time_signature_cb = set_time_signature_func
        self.set_pitch_cb = set_pitch_func
        self.set_rest_cb = set_rest_func
        self.set_lyric_cb = set_lyric_func
        self.set_tie_cb = set_tie_func
        self.set_dot_cb = set_dot_func
        self.set_tuplet_cb = set_tuplet_func

        tree = ET.parse(xml_file)
        root = tree.getroot()
        self.parse_root(root)
        return root
