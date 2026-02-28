import csv


def write_launch_info_to_csv(
    *,
    parsed_methods: list[str],
    output_file: str,
) -> None:
    with open(output_file, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["dll", "method"])

        for item in parsed_methods:
            if "," in item:
                dll, method = item.split(",", 1)
                writer.writerow([dll, method])
