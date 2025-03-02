from cape_parsers.CAPE.core.DoppelPaymer import extract_config, rule_source
from maco.extractor import Extractor
from maco.model import ExtractorModel as MACOModel

from modules.parsers.utils import get_YARA_rule


def convert_to_MACO(raw_config: dict):
    if not (raw_config and isinstance(raw_config, dict)):
        return None

    parsed_result = MACOModel(family="DoppelPaymer")

    if "strings" in raw_config:
        parsed_result.decoded_strings = raw_config["strings"]

    if "RSA public key" in raw_config:
        parsed_result.encryption.append(MACOModel.Encryption(algorithm="RSA", public_key=raw_config["RSA public key"]))

    return parsed_result


class DoppelPaymer(Extractor):
    author = "kevoreilly"
    family = "DoppelPaymer"
    last_modified = "2024-10-26"
    sharing = "TLP:CLEAR"
    yara_rule = get_YARA_rule(family)

    yara_rule = rule_source

    def run(self, stream, matches):
        return convert_to_MACO(extract_config(stream.read()))
