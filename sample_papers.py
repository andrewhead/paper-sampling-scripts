import argparse
import dataclasses
import json
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List

import requests

from .common import CONFERENCE_IDS_DIR, OUTPUT_DIR


@dataclass(frozen=True)
class Paper:
    id_: str
    title: str
    arxiv_id: str
    arxiv_link: str


# Semantic Scholar requests that no more than 100 requests be made to the API every 5 minutes
# from a single IP address.
SEMANTIC_SCHOLAR_REQUEST_DELAY = 200  # milliseconds


def fetch_paper_details(
    ids: List[str], min_citation_velocity: int, verbose: bool = True
) -> Iterator[Paper]:

    first_request = True

    for id_ in ids:

        if not first_request:
            time.sleep(SEMANTIC_SCHOLAR_REQUEST_DELAY)
        if verbose:
            print(f"Fetching data from Semantic Scholar for paper {id_}.")
        response = requests.get(f"https://api.semanticscholar.org/v1/paper/{id_}")
        if first_request:
            first_request = False

        if response.ok:
            paper_json = response.json()

            if paper_json["arxivId"] is None:
                if verbose:
                    print(
                        f"Semantic Scholar does not have an arXiv ID for {id_}. "
                        + "Paper will not be sampled."
                    )
                continue
            if paper_json["citationVelocity"] < min_citation_velocity:
                if verbose:
                    print(
                        f"Paper {id_} has a low citation velocity ({paper_json['citationVelocity']}"
                        + f"< {min_citation_velocity}). Paper will not be sampled."
                    )
                continue

            yield Paper(
                id_=id_,
                title=paper_json["title"],
                arxiv_id=paper_json["arxivId"],
                arxiv_link=f"https://arxiv.org/pdf/{paper_json['arxivId']}.pdf",
            )


if __name__ == "__main__":

    argument_parser = argparse.ArgumentParser(
        description=(
            "Sample papers from recent conference proceedings. Chooses those papers that have "
            + "an arXiv ID and a sufficiently high citation velocity."
        )
    )
    argument_parser.add_argument(
        "--papers-per-conference",
        help=(
            "The number of papers to sample for each conference. Note that the time to run this "
            + "script will increase linearly with the number of papers to sample, as each paper will "
            + "require a separate request to the Semantic Scholar API."
        ),
        type=int,
        default=50,
    )
    argument_parser.add_argument(
        "--min-citation-velocity",
        help="Minimum citation velocity for a paper to be included in the sample.",
        type=int,
        default=10,
    )
    argument_parser.add_argument(
        "--seed",
        default=42,
        type=int,
        help=(
            "Random seed to be used when sampling papers. Set this value to either replicate a "
            + "sample made previously, or to request a different sample than what was sampled before."
        ),
    )
    argument_parser.add_argument()
    args = argument_parser.parse_args()
    RANDOM_SEED = args.seed

    if not os.path.exists(CONFERENCE_IDS_DIR):
        raise SystemExit(
            "No directory found containing lists of IDs of papers at conferences. "
            + "Run 'extract_papers_for_conferences.py' before this script."
        )

    SAMPLED_IDS_DIR = os.path.join(OUTPUT_DIR, "sampled-ids")
    for filename in os.listdir(CONFERENCE_IDS_DIR):
        with open(os.path.join(CONFERENCE_IDS_DIR, filename)) as ids_file:
            ids = [l.strip() for l in ids_file.read()]

        # Make the shuffling of IDs for a conference deterministic by combining the user-specified
        # seed with a hash for the conference name.
        random.seed(args.seed * hash(filename))
        ids_shuffled = list(ids)
        random.shuffle(ids_shuffled)

        # Samples will not necessarily be exactly the same every time this script is run, because
        # the data for a paper on Semantic Scholar might change (for instance, the citation
        # velocity for a paper, or the presence of an arXiv ID for a paper).
        sample = []
        for paper in fetch_paper_details(ids_shuffled, args.min_citation_velocity):
            sample.append(paper)
            if len(sample) > args.papers_per_conference:
                break

        print(f"Sampled {len(sample)} papers for conference {filename}")
        if len(sample) > 0:
            if not os.path.exists(SAMPLED_IDS_DIR):
                os.makedirs(SAMPLED_IDS_DIR)
            with open(
                os.path.join(SAMPLED_IDS_DIR, filename), encoding="utf-8", mode="w"
            ) as sample_file:
                for paper in sample:
                    sample_file.write(json.dumps(dataclasses.asdict(paper)) + "\n")
