# coding: utf-8
"""Converts an RTF string into an into an XML string created by rtf2xml."""

import io
import os

import rtf2xml.ParseRtf


class Rtf2XmlConverter(object):
    def convert(self, rtf):
        input_path = os.path.join('tmp', 'in.rtf')
        output_path = os.path.join('tmp', 'out.xml')
        # Write the RTF string to a temporary file.
        with open(input_path, 'wb') as f:
            f.write(rtf)

        # Convert the RTF string to an XML string.
        parse_obj = rtf2xml.ParseRtf.ParseRtf(
            in_file=input_path,
            out_file=output_path,  # determine the output file
            run_level=1,  # determine the run level. The default is 1.
            indent=1,  # Indent resulting XML. Default is 0 (no indent).
            headings_to_sections=1,  # Convert headings to sections. Default is 0.
            group_styles=0,  # Group paragraphs with the same style name. Default is 1.
            empty_paragraphs=1,  # Write or do not write paragraphs. Default is 0.
        )
        parse_obj.parse_rtf()
        with io.open(output_path, mode='r', encoding='utf-8') as f:
            rtf2xml_string = f.read()
            # print rtf_xmlstring
            # sys.exit()

        if len(os.listdir('tmp')) > 2:
            raise NotImplementedError('Additional media detected in the RTF->XML output dir, which is not supported')

        return rtf2xml_string
