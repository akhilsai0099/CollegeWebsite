from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import BatchCode
import csv


# def upload_data_from_csv(request, model, batchCode, field_mappings):
#     csv_file = request.FILES.get("csv_upload")
#     batch_code = request.POST.get("batchCode")

#     if not csv_file:
#         messages.warning(request, "Please upload a CSV file")
#         return HttpResponseRedirect(request.path_info)

#     if not csv_file.name.endswith(".csv"):
#         messages.warning(request, "Please upload a CSV file")
#         return HttpResponseRedirect(request.path_info)

#     decoded_file = csv_file.read().decode("utf-8").splitlines()
#     reader = csv.reader(decoded_file)

#     for row in reader:
#         try:
#             data_fields = {}
#             for mapping in field_mappings:
#                 csv_field = mapping[0]
#                 model_field = mapping[1]
#                 if row[csv_field] == "":
#                     data_fields[model_field] = None
#                 else:
#                     data_fields[model_field] = row[csv_field]
#             userdata, created = model.objects.update_or_create(
#                 rollno=data_fields["rollno"], defaults=data_fields)

#             if created:
#                 messages.success(request, f"Data added")
#             else:
#                 messages.success(request, f"Data updated")
#         except Exception as e:
#             print(e)
#             messages.error(request, f"Error updating/adding data - {str(e)}")

#     messages.success(request, "Data has been uploaded from the CSV file")
#     return HttpResponseRedirect(request.path_info)

def upload_data_from_csv(request, model, batchCode, field_mappings):
    csv_file = request.FILES.get("csv_upload")

    if not csv_file:
        messages.warning(request, "Please upload a CSV file")
        return HttpResponseRedirect(request.path_info)

    if not csv_file.name.endswith(".csv"):
        messages.warning(request, "Please upload a CSV file")
        return HttpResponseRedirect(request.path_info)

    decoded_file = csv_file.read().decode("utf-8").splitlines()
    reader = csv.reader(decoded_file)

    for row in reader:
        try:
            data_fields = {}
            for mapping in field_mappings:
                csv_field = mapping[0]
                model_field = mapping[1]
                if row[csv_field] == "":
                    data_fields[model_field] = None
                else:
                    data_fields[model_field] = row[csv_field]
            data_fields['batchCode'] = batchCode
            userdata, created = model.objects.update_or_create(
                rollno=data_fields["rollno"], defaults=data_fields)

            if created:
                messages.success(request, f"Data added")
            else:
                messages.success(request, f"Data updated")
        except Exception as e:
            print(e)
            messages.error(request, f"Error updating/adding data - {str(e)}")

    messages.success(request, "Data has been uploaded from the CSV file")
    return HttpResponseRedirect(request.path_info)