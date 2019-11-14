from .alphago import AlphaGoEncoder
from .encoder import Encoder
from .oneplane import OnePlaneEncoder
from .sevenplane import SevenPlaneEncoder
from .simple import SimpleEncoder

encoders_by_name = {
    'oneplane': OnePlaneEncoder,
    'sevenplane': SevenPlaneEncoder,
    'simple': SimpleEncoder,
    'alphago': AlphaGoEncoder,
    'betago': SevenPlaneEncoder
}

for n, e in encoders_by_name.items():
    e.name = n


def get_encoder(name, board_size):
    return encoders_by_name[name](board_size)
