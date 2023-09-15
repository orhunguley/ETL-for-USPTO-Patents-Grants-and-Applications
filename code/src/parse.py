import argparse
import sys


def parse_args():
    """
    r
    """
    parser = argparse.ArgumentParser(
        description="Provide SlowFast video training and testing pipeline.")

    parser.add_argument(
        "-d",
        "--patent-type",
        default="application",
        type=str,
        choices=['application', 'grant'],
        help="Ingesting grant/application data",
    )
    
    return parser.parse_args()



