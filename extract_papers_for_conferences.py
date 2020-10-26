import argparse
import gzip
import json
import os.path
from dataclasses import dataclass
from typing import Dict, List

from .common import CONFERENCE_IDS_DIR, DATA_DIR, OUTPUT_DIR


@dataclass(frozen=True)
class Conference:
    venue: str
    year: int


CONFERENCES = [
    Conference("NeurIPS", 2017),
    Conference("NeurIPS", 2018),
    Conference("NeurIPS", 2019),
    Conference("ACL", 2017),
    Conference("ACL", 2018),
    Conference("ACL", 2019),
    Conference("CVPR", 2017),
    Conference("CVPR", 2018),
    Conference("CVPR", 2019),
    Conference("ICML", 2017),
    Conference("ICML", 2018),
    Conference("ICML", 2019),
]


PaperId = str


def get_papers_by_conference(
    corpus_file_paths, conferences: List[Conference]
) -> Dict[Conference, List[PaperId]]:

    papers_by_conference: Dict[Conference, List[PaperId]] = {c: [] for c in conferences}

    for path in corpus_file_paths:
        with gzip.open(path, "rb") as corpus_file:

            for line in corpus_file:
                paper = json.loads(line.strip())
                if paper["venue"] == "" or paper["year"] == "":
                    continue

                paper_id = paper["id"]
                conference = Conference(paper["venue"], paper["year"])
                if conference in conferences:
                    papers_by_conference[conference].append(paper_id)

    return papers_by_conference


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="")
    argument_parser.add_argument(
        "semantic_scholar_corpus_gzip_files",
        nargs="+",
        help=(
            "paths to gzipped files in the Semantic Scholar Open Research Corpus. These files "
            + "can be downloaded from here http://s2-public-api-prod.us-west-2.elasticbeanstalk.com/corpus/download/."
        ),
    )

    args = argument_parser.parse_args()
    papers_by_conference = get_papers_by_conference(
        args.semantic_scholar_corpus_gzip_files, CONFERENCES
    )

    for conference, paper_ids in papers_by_conference.items():
        conference_ids_path = os.path.join(
            CONFERENCE_IDS_DIR, f"{conference.venue}-{conference.year}"
        )
        print(
            f"Found {len(paper_ids)} papers for conference {conference.venue} {conference.year}."
        )

        if len(paper_ids) > 0:
            if not os.path.exists(CONFERENCE_IDS_DIR):
                os.makedirs(CONFERENCE_IDS_DIR)

            print(
                f"Saving IDs for papers for this conference to {conference_ids_path}."
            )
            with open(conference_ids_path, "w") as conference_ids_file:
                for i, id_ in enumerate(paper_ids):
                    conference_ids_file.write(id_)
                    if i < len(paper_ids) - 1:
                        conference_ids_file.write("\n")
