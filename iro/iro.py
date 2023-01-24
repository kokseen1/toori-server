import argparse

from iro.main import start


def main():
    parser = argparse.ArgumentParser(description="Iro")
    parser.add_argument("port", type=int, default=80)
    parser.add_argument("-c", "--certs", type=str, required=False)

    args = parser.parse_args()

    start(args.port, args.certs)


if __name__ == "__main__":
    main()
