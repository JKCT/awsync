"AWS type models."
from awsync.models.strenum import StrEnum
from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass(frozen=True)
class Credentials:
    "AWS Credentials."
    access_key_id: str
    "The Access Key ID."
    secret_access_key: str = field(repr=False)  # Avoid logging secret values.
    "The Secret Access Key."
    session_token: Optional[str] = None
    "(Optional) The session security token if using temporary credentials."

    @classmethod
    def from_environment(cls) -> "Credentials":
        try:
            return cls(
                access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                session_token=os.environ.get("AWS_SESSION_TOKEN"),
            )
        except KeyError as exc:
            raise KeyError(
                "Unable to find AWS credentials in environment variables when calling Credentials.from_environment(). "
                "Ensure environment variables 'AWS_ACCESS_KEY_ID' and 'AWS_SECRET_ACCESS_KEY' are set before calling Credentials.from_environment() or use Credentials() to set values directly."
            ) from exc


class Region(StrEnum):
    """
    An AWS Region.
    See: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions
    """

    us_east_1 = "us-east-1"
    "US East (Virginia)"
    us_east_2 = "us-east-2"
    "US East (Ohio)"
    us_west_1 = "us-west-1"
    "US West (N. California)"
    us_west_2 = "us-west-2"
    "US West (Oregon)"
    af_south_1 = "af-south-1"
    "Africa (Cape Town)"
    ap_east_1 = "ap-east-1"
    "Asia Pacific (Hong Kong)"
    ap_south_2 = "ap-south-2"
    "Asia Pacific (Hyderabad)"
    ap_southeast_3 = "ap-southeast-3"
    "Asia Pacific (Jakarta)"
    ap_southeast_4 = "ap-southeast-4"
    "Asia Pacific (Melbourne)"
    ap_south_1 = "ap-south-1"
    "Asia Pacific (Mumbai)"
    ap_northeast_3 = "ap-northeast-3"
    "Asia Pacific (Osaka)"
    ap_northeast_2 = "ap-northeast-2"
    "Asia Pacific (Seoul)"
    ap_southeast_1 = "ap-southeast-1"
    "Asia Pacific (Singapore)"
    ap_southeast_2 = "ap-southeast-2"
    "Asia Pacific (Sydney)"
    ap_northeast_1 = "ap-northeast-1"
    "Asia Pacific (Tokyo)"
    ca_central_1 = "ca-central-1"
    "Canada (Central)"
    ca_west_1 = "ca-west-1"
    "Canada West (Calgary)"
    eu_central_1 = "eu-central-1"
    "Europe (Frankfurt)"
    eu_west_1 = "eu-west-1"
    "Europe (Ireland)"
    eu_west_2 = "eu-west-2"
    "Europe (London)"
    eu_south_1 = "eu-south-1"
    "Europe (Milan)"
    eu_west_3 = "eu-west-3"
    "Europe (Paris)"
    eu_south_2 = "eu-south-2"
    "Europe (Spain)"
    eu_north_1 = "eu-north-1"
    "Europe (Stockholm)"
    eu_central_2 = "eu-central-2"
    "Europe (Zurich)"
    il_central_1 = "il-central-1"
    "Israel (Tel Aviv)"
    me_south_1 = "me-south-1"
    "Middle East (Bahrain)"
    me_central_1 = "me-central-1"
    "Middle East (UAE)"
    sa_east_1 = "sa-east-1"
    "South America (São Paulo)"
