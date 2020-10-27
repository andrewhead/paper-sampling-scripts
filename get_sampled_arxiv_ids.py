import argparse
import json
import os.path
from collections import defaultdict
from typing import Dict, List

from common import OUTPUT_DIR

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Extract arXiv IDs for all sampled papers."
    )
    argument_parser.add_argument(
        "sample_files",
        nargs="+",
        help="paths to all sample files from which to extract arXiv IDs",
    )
    argument_parser.add_argument(
        "--conference-comments",
        action="store_true",
        help=(
            "write a comment (denoted by '#') next to each arXiv ID denoting "
            "the conference that paper was sampled for."
        ),
    )
    args = argument_parser.parse_args()

    arxiv_ids_by_conference: Dict[str, List] = defaultdict(list)
    for path in args.sample_files:
        with open(path, encoding="utf-8") as sample_file:
            conference_name = os.path.basename(path)
            for line in sample_file:
                paper_data = json.loads(line.strip())
                arxiv_ids_by_conference[conference_name].append(paper_data["arxiv_id"])

    if len(arxiv_ids_by_conference) > 0:
        output_path = os.path.join(OUTPUT_DIR, "sampled-arxiv-ids")
        with open(output_path, mode="w") as arxiv_ids_file:
            for conference, arxiv_ids in arxiv_ids_by_conference.items():
                for arxiv_id in arxiv_ids:
                    arxiv_ids_file.write(arxiv_id)
                    if args.conference_comments:
                        arxiv_ids_file.write(f"  # {conference}")
                    arxiv_ids_file.write("\n")
