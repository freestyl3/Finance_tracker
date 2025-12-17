import csv
import io

def generate_csv_report(data: dict) -> io.StringIO:
    output = io.StringIO()

    writer = csv.writer(output, delimiter=';')

    output.write('\ufeff')

    writer.writerow(["Total expenses", str(data["total_sum"]).replace('.', ',')])
    writer.writerow([])

    writer.writerow(["Category ID", "Category name", "Amount"])

    for row in data["categories"]:
        writer.writerow([
            row["category_id"],
            row.get("category_name", "Unknown"),
            str(row["total_amount"]).replace('.', ',')
        ])

    output.seek(0)

    return output
