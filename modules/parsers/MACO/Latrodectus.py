from cape_parsers.CAPE.core.Latrodectus import extract_config
from maco.extractor import Extractor
from maco.model import ExtractorModel as MACOModel

from modules.parsers.utils import get_YARA_rule


def convert_to_MACO(raw_config: dict):
    if not (raw_config and isinstance(raw_config, dict)):
        return None

    parsed_result = MACOModel(family="Latrodectus", other=raw_config)

    for c2_url in raw_config.get("C2", []):
        parsed_result.http.append(MACOModel.Http(uri=c2_url, usage="c2"))

    if "Group name" in raw_config:
        parsed_result.identifier.append(raw_config["Group name"])

    if "Campaign ID" in raw_config:
        parsed_result.campaign_id.append(str(raw_config["Campaign ID"]))

    if "Version" in raw_config:
        parsed_result.version = raw_config["Version"]

    if "RC4 key" in raw_config:
        parsed_result.encryption.append(MACOModel.Encryption(algorithm="RC4", key=raw_config["RC4 key"]))

    if "Strings" in raw_config:
        parsed_result.decoded_strings = raw_config["Strings"]

    return parsed_result


class Latrodectus(Extractor):
    author = "kevoreilly"
    family = "Latrodectus"
    last_modified = "2024-10-26"
    sharing = "TLP:CLEAR"
    yara_rule = get_YARA_rule(family)

    def run(self, stream, matches):
        return convert_to_MACO(extract_config(stream.read()))
