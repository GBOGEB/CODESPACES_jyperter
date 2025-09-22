import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="default", help="pipeline profile")
    args = parser.parse_args()
    print(f"Running pipeline with profile {args.profile}")

if __name__ == "__main__":
    main()
