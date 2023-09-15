import argparse
import sys


def parse_args():
    """
    Parse command-line arguments for the SlowFast video training and testing pipeline.

    Returns:
        argparse.Namespace: An object containing parsed command-line arguments.

    This function sets up an argparse argument parser to handle command-line options
    and arguments for the SlowFast video training and testing pipeline. It allows users
    to specify the type of patent data they want to process, either 'application' or 'grant'.

    Returns the parsed command-line arguments as an argparse.Namespace object.
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



