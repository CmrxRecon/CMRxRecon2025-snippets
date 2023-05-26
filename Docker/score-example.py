 #!/usr/bin/env python3
import json
import argparse

def get_args():
    """Set up command-line interface and get arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--submissionfile", type=str, required=True, help="Submission File")
    parser.add_argument("-g", "--goldstandard", type=str,required=True, help="Goldstandard for scoring")
    parser.add_argument("-r", "--results", type=str, required=True, default="results.json", help="Scoring results")
    return parser.parse_args()

def main():
    """Main function."""
    args = get_args()
    
    scores = {
        "LV_dsc": 0.91, 
        "MYO_dsc": 0.92,
        "RV_dsc": 0.93,
        "LV_hd95": 0.94,
        "MYO_hd95": 0.95,
        "RV_hd95": 0.96
    }

    with open(args.results, "w") as out:
        results = {
            "submission_status": "SCORED",
            "submission_errors": "No errors!",
            **scores
        }
        out.write(json.dumps(results))

if __name__ == "__main__":
    main()
