"""
Script that is called to run the indexer, the searcher and the evaluator.

Made by: José Gonçalves nº84967
"""

import searching
from arguments import get_arguments, print_arguments
from definitions import IndexingFormat, IndexingStatistics, SearchResults
from evaluating import Evaluator
from store import idxprops, index, segments
from indexing import indexing

import utils


def main():
    _arguments = get_arguments()
    print_arguments(_arguments)

    if _arguments.indexing_format != IndexingFormat.NO_INDEX:
        index_stats = indexing.create_index(_arguments)
        print_statistics(index_stats)
    else:
        print("[main]: Skipping indexing phase.")

    if not _arguments.index_only:
        print(f"[main]: Searching queries in '{_arguments.queries_path}'.")
        print(f"[main]: Writing results to '{_arguments.results_path}'")
        index_directory = index.IndexDirectory(_arguments.index_path)
        index_properties = idxprops.read_props(index_directory.idx_props_path)
        index_segments = segments.read_segments(index_directory.segments_dir_path)
        search_func = searching.get_searcher(
            index_properties.idx_format,
            index_properties.min_token_length,
            index_properties.stopwords,
            index_properties.stemmer,
            index_segments,
            index_directory.review_ids_path
        )
        queries = read_queries_file(_arguments.queries_path)
        evaluator = Evaluator(_arguments.queries_rev_path, search_func, _arguments.query_limit)

        for query in queries:
            # results = search_func(query)
            results = evaluator.search(query)
            write_results(
                f"RESULT FOR QUERY '{query}'",
                results,
                _arguments.results_path
            )

        evaluator.output_evaluation(_arguments.evaluation_path)
    else:
        print("[main]: Skipping Searching queries phase.")


def print_statistics(indexing_statistics: IndexingStatistics):
    print(f"Indexing time: {utils.format_time_interval(indexing_statistics.indexing_time)}")
    print(f"Index size: {indexing_statistics.index_size_on_disk / 1024 / 1024} MB")
    print(f"Temporary Blocks Used: {indexing_statistics.blocks_used}")
    print(f"Term Count: {indexing_statistics.term_count}")
    print(f"Review Count: {indexing_statistics.review_count}")


def read_queries_file(queries_path: str):
    with open(queries_path, encoding="utf-8") as queries_file:
        return [query.strip().lower() for query in queries_file]


def write_results(
        heading: str,
        search_results: SearchResults,
        results_path: str
):
    with open(results_path, "a", encoding="utf-8", newline="\n") as results_file:
        results_file.write(f"=== {heading} ===\n\n\n")
        results_file.write(f"{'REVIEW ID':>20}  {'SCORE':>20}\n\n")
        for review_id, score in search_results:
            results_file.write(f"{review_id:>20}  {score:>20}\n")

        results_file.write("\n\n\n\n")


if __name__ == "__main__":
    main()
