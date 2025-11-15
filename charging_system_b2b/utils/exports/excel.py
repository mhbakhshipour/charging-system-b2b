import xlwt
import base64

from django.http import HttpResponse, JsonResponse


def escape_value(value):
    # Escape special characters for Excel
    value = str(value)
    value = value.replace('"', '""')
    value = value.replace("@", "[@]")
    value = value.replace("+", "[+]")
    value = value.replace("-", "[-]")
    value = value.replace("=", "[=]")
    value = value.replace("|", "[|]")
    value = value.replace("%", "[%]")
    return value


def export_excel(
    data, data_type="normal", sheet_name="sheet", file_name="file", for_download=False
):
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet(sheet_name)

    response = HttpResponse(content_type="application/ms-excel")

    if data_type == "list" and data:
        header_values = data[0].keys()
        for counter, value in enumerate(header_values):
            sanitized_value = escape_value(value)  # Escape the header value
            ws.write(0, counter, sanitized_value)

        for row_counter, row in enumerate(data, 1):
            cell_values = row.values()
            for cell_counter, cell in enumerate(cell_values):
                sanitized_cell = escape_value(cell)  # Escape the cell value
                ws.write(row_counter, cell_counter, sanitized_cell)

    elif data_type == "dict" and data:
        header_values = data.keys()
        for counter, value in enumerate(header_values):
            sanitized_value = escape_value(value)  # Escape the header value
            ws.write(0, counter, sanitized_value)

        cell_values = data.values()
        for counter, cell in enumerate(cell_values, 1):
            sanitized_cell = escape_value(cell)  # Escape the cell value
            ws.write(1, counter, sanitized_cell)

    else:
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                sanitized_value = escape_value(value)  # Escape the cell value
                ws.write(row_idx, col_idx, sanitized_value)

    wb.save(response)

    if for_download:
        response["Content-Disposition"] = f"attachment; filename={file_name}.xls"
        return response

    encoded_string = base64.b64encode(response.content).decode("utf-8")
    return JsonResponse(
        status=200,
        data={"data": f"data:application/vnd.ms-excel;base64,{encoded_string}"},
    )
