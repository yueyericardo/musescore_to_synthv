import re
import xml.etree.ElementTree as ET

ONE_BEAT = 705600000


class txt:
    CEND = "\033[0m"
    CBOLD = "\33[1m"
    CITALIC = "\33[3m"
    CURL = "\33[4m"
    CBLINK = "\33[5m"
    CBLINK2 = "\33[6m"
    CSELECTED = "\33[7m"

    CBLACK = "\33[30m"
    CRED = "\33[31m"
    CGREEN = "\33[32m"
    CYELLOW = "\33[33m"
    CBLUE = "\33[34m"
    CVIOLET = "\33[35m"
    CBEIGE = "\33[36m"
    CWHITE = "\33[37m"

    CBLACKBG = "\33[40m"
    CREDBG = "\33[41m"
    CGREENBG = "\33[42m"
    CYELLOWBG = "\33[43m"
    CBLUEBG = "\33[44m"
    CVIOLETBG = "\33[45m"
    CBEIGEBG = "\33[46m"
    CWHITEBG = "\33[47m"

    CGREY = "\33[90m"
    CRED2 = "\33[91m"
    CGREEN2 = "\33[92m"
    CYELLOW2 = "\33[93m"
    CBLUE2 = "\33[94m"
    CVIOLET2 = "\33[95m"
    CBEIGE2 = "\33[96m"
    CWHITE2 = "\33[97m"

    TAB = "  "


jp_to_hr = {
    "a": "aa",
    "b": "b",
    "c": "z",
    "č": "ch",
    "ć": "ch",
    "d": "d",
    "dž": "",
    "đ": "jh",
    "e": "eh",
    "f": "f",
    "g": "g",
    "h": "hh",
    "i": "iy",
    "j": "y",
    "k": "k",
    "l": "l",
    "lj": "",
    "m": "m",
    "n": "n",
    "nj": "",
    "o": "ow",
    "p": "p",
    "r": "r",
    "s": "s",
    "š": "sh",
    "t": "t",
    "u": "uw",
    "v": "v",
    "z": "z",
    "ž": "zh",
}


def get_time_signature_duration(n, d):
    # print("get_time_signature_duration")
    if n == 4 and d == 4:
        return int(ONE_BEAT * 4)
    elif n == 3 and d == 4:
        return int(ONE_BEAT * 3)
    elif n == 6 and d == 8:
        return int(6 * int(ONE_BEAT / 2))


class XMLParser:
    def __init__(self, readfile, verbose=False, use_hr_dict=False):
        self.verbose = verbose
        self.xml_file = readfile
        self.use_hr_dict = use_hr_dict

        self.pitch = 0
        self.duration = 0
        self.onset = 0
        self.lyric = ""
        self.comment = ""
        self.tie = False
        self.dot = 0
        self.staff_num = 0
        self.tuplet = False
        self.output_string = ""

        self.SET_TAB = txt.TAB * 30

        self.duration_type = {
            "measure": None,
            "whole": int(ONE_BEAT * 4),
            "half": int(ONE_BEAT * 2),
            "quarter": int(ONE_BEAT),
            "eighth": int(ONE_BEAT / 2),
            "16th": int(ONE_BEAT / 4),
            "32nd": int(ONE_BEAT / 8),
        }

    def generate_lyric(self, l):
        if l in ["-", "", "", None]:
            return "-"
        if self.use_hr_dict:
            string = "."
            for letter in l:
                try:
                    string += jp_to_hr[letter.lower()] + " "
                except KeyError:
                    pass
            return string[:-1]
        return re.sub(r"\W+", "", l)

    def generate_project_start(self):
        string = ""
        string += "{" + "\n"
        string += '    "version": 7,' + "\n"
        string += '    "meter": [' + "\n"
        string += "        {" + "\n"
        string += '            "measure": 0,' + "\n"
        string += '            "beatPerMeasure": 4,' + "\n"
        string += '            "beatGranularity": 4' + "\n"
        string += "        }" + "\n"
        string += "    ]," + "\n"
        string += '    "tempo": [' + "\n"
        string += "        {" + "\n"
        string += '            "position": 0,' + "\n"
        string += '            "beatPerMinute": 90.0' + "\n"
        string += "        }" + "\n"
        string += "    ]," + "\n"
        string += '    "tracks": [' + "\n"
        return string

    def generate_staff_start(self):
        string = ""
        string += "        {" + "\n"
        string += '            "name": "Unnamed Track",' + "\n"
        string += '            "dbName": "Eleanor Forte",' + "\n"
        string += '            "color": "15e879",' + "\n"
        string += '            "displayOrder": ' + str(self.staff_num) + "," + "\n"
        string += '            "dbDefaults": {},' + "\n"
        string += '            "notes": [' + "\n"
        return string

    def generate_note(self):
        string = ""
        string += "                {" + "\n"
        string += '                    "onset": ' + str(self.onset) + "," + "\n"
        string += '                    "duration": ' + str(self.duration) + "," + "\n"
        string += (
            '                    "lyric": "'
            + self.generate_lyric(self.lyric)
            + '",'
            + "\n"
        )
        string += '                    "comment": "' + str(self.lyric) + '",' + "\n"
        string += '                    "pitch": ' + str(self.pitch) + "," + "\n"
        string += '                    "dF0Vbr": 0.0' + "," + "\n"
        string += '                    "dF0Jitter": 0.0' + "" + "\n"
        string += "                }," + "\n"
        return string

    def generate_staff_end(self):
        string = ""
        string += "            ]," + "\n"
        string += '            "gsEvents": null,' + "\n"
        string += '            "mixer": {' + "\n"
        string += '                "gainDecibel": 0.0,' + "\n"
        string += '                "pan": 0.0,' + "\n"
        string += '                "muted": false,' + "\n"
        string += '                "solo": false,' + "\n"
        string += '                "engineOn": true,' + "\n"
        string += '                "display": true' + "\n"
        string += "            }," + "\n"
        string += '            "parameters": {' + "\n"
        string += '                "interval": 5512500,' + "\n"
        string += '                "pitchDelta": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "vibratoEnv": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "loudness": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "tension": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "breathiness": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "voicing": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]," + "\n"
        string += '                "gender": [' + "\n"
        string += "                    0," + "\n"
        string += "                    0" + "\n"
        string += "                ]" + "\n"
        string += "            }" + "\n"
        string += "        }," + "\n"
        return string

    def generate_project_end(self):
        string = ""
        string += "    ]," + "\n"
        string += '    "instrumental": {' + "\n"
        string += '        "filename": "",' + "\n"
        string += '        "offset": 0.0' + "\n"
        string += "    }," + "\n"
        string += '    "mixer": {' + "\n"
        string += '        "gainInstrumentalDecibel": 0.0,' + "\n"
        string += '        "gainVocalMasterDecibel": 0.0,' + "\n"
        string += '        "instrumentalMuted": false,' + "\n"
        string += '        "vocalMasterMuted": false' + "\n"
        string += "    }" + "\n"
        string += "}" + "\n"
        return string

    def set_staff_start(self):
        self.onset = 0
        self.output_string += self.generate_staff_start()

    def set_staff_end(self):
        self.output_string += self.generate_staff_end()
        self.staff_num += 1

    def set_time_signature(self, n, d):
        self._print_verbose(
            self.SET_TAB + txt.CRED + "set_time_signature" + txt.CEND, n, d
        )
        time_signature_n = int(n)
        time_signature_d = int(d)
        self.duration_type["measure"] = get_time_signature_duration(
            time_signature_n, time_signature_d
        )

    def set_pitch(self, p, d):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_pitch" + txt.CEND, p, d)

        self.pitch = int(p)
        self.duration += self.duration_type[d]

        if self.dot > 0:
            self.duration += int(self.duration_type[d] / 2)
        if self.dot > 1:
            self.duration += int(self.duration_type[d] / 4)
        if self.dot > 2:
            self.duration += int(self.duration_type[d] / 8)
        self.dot = 0

        if self.tuplet:
            self.duration = self.duration * 2 / 3

        if self.tie:
            self.tie = False
        else:
            if self.lyric == "":
                self.lyric = "-"
            # print(generate_note())
            self.output_string += self.generate_note()
            self.onset += self.duration
            self.duration = 0
            self.lyric = ""

    def set_rest(self, d):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_rest" + txt.CEND, d)
        duration = self.duration_type[d]

        if self.dot > 0:
            duration += int(self.duration_type[d] / 2)
        if self.dot > 1:
            duration += int(self.duration_type[d] / 4)
        if self.dot > 2:
            duration += int(self.duration_type[d] / 8)
        self.dot = 0

        if self.tuplet:
            duration = duration * 2 / 3

        self.onset += duration

    def set_lyric(self, l):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_lyric" + txt.CEND, l)
        self.lyric = l

    def set_tie(self):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_tie" + txt.CEND)
        self.tie = True

    def set_dot(self, num):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_dot" + txt.CEND, num)
        self.dot = int(num)

    def set_tuplet(self, status):
        self._print_verbose(self.SET_TAB + txt.CRED + "set_tuplet" + txt.CEND, status)
        if status:
            self.tuplet = True
        else:
            self.tuplet = False

    def _print_verbose(self, *args):
        if self.verbose:
            print(*args)

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

    def parse_rest(self, v):
        for r in v.findall("./"):
            self._print_verbose(
                txt.TAB * 4,
                txt.CBEIGE + r.tag + txt.CEND,
                [r.attrib, r.tail.strip(), str(r.text).strip()],
            )
            if r.tag == "durationType":
                self.set_rest(r.text)

    def parse_root(self, r):
        for s in r.findall("./Score/Staff"):
            self._print_verbose(
                txt.CBLUE + s.tag + txt.CEND,
                [s.attrib, s.tail.strip(), str(s.text).strip()],
            )
            m_count = 0
            self.set_staff_start()
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

            self.set_staff_end()

    def parse_xml(self):
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        self.output_string += self.generate_project_start()
        self.parse_root(root)
        self.output_string += self.generate_project_end()
        return root
