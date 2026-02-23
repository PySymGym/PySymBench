import csv

from backend.utils.methods_handler import Methods


def write_launch_info_csv(
    *,
    methods: list[str],
    dataset_methods: Methods,
    output_file: str,
) -> None:
    parsed = dataset_methods.get_methods_from_selection(methods)

    with open(output_file, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["dll", "method"])

        for item in parsed:
            if "," in item:
                dll, method = item.split(",", 1)
                writer.writerow([dll, method])
