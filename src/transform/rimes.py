"""
Transform Rimes dataset
"""

import os
from data import preproc
import xml.etree.ElementTree as ET
import html


class Transform():

    def __init__(self, source, charset, max_text_length):
        self.source = source
        self.charset = charset
        self.max_text_length = max_text_length
        self.lines = dict()
        self.partitions = dict()

    def build(self):
        train = self._build_partition("training_2011.xml")

        total = len(train)
        train_i = int(total * 0.8)
        valid_i = train_i + int((total - train_i) / 2)

        self.partitions["train"] = train[:train_i]
        self.partitions["valid"] = train[train_i:valid_i]
        self.partitions["test"] = self._build_partition("eval_2011_annotated.xml")

    def _build_partition(self, partition):
        xml = ET.parse(os.path.join(self.source, partition)).getroot()
        lines = []

        for page_tag in xml:
            for i, line_tag in enumerate(page_tag.iter("Line")):
                text_line = " ".join(html.unescape(line_tag.attrib["Value"]).split())

                if len(text_line) > 0:
                    lines.append(text_line)

        lines = list(set(lines))
        lines = preproc.normalize_text(lines, charset=self.charset, limit=self.max_text_length)

        return lines