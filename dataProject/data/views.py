
import json
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import infer_and_convert_data_types, get_user_friendly_dtype, serialise_dataframe, override_data, column_type_overrides
import pandas as pd
import traceback
from django.core.serializers.json import DjangoJSONEncoder
from django.core.files.base import ContentFile

from .models import Dataset
import traceback

last_uploaded_df = None

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        datafile = request.FILES.get('datafile', None)
        if datafile is None:
            return JsonResponse({'error': 'No file provided.'}, status=400)

        try:
            if str(datafile.name).lower().endswith('.csv'):
                df = pd.read_csv(datafile)
            elif str(datafile.name).lower().endswith('.xlsx'):
                df = pd.read_excel(datafile)
            else:
                return JsonResponse({'error': 'Unsupported file format. Only .csv and .xlsx are supported.'}, status=400)

            # get processed data
            # convert data types to user friendly names
            processed_df = infer_and_convert_data_types(df)
            processed_data_list = serialise_dataframe(processed_df)
            processed_data_pkl = pickle.dumps(processed_df)
            columns_with_types = [{'column': col, 'data_type': get_user_friendly_dtype(dtype)} for col, dtype in zip(processed_df.columns, processed_df.dtypes)]
            # Serialize dataframe using pickle
            processed_data_pkl = pickle.dumps(processed_df)

            # Save the uploaded data and column types to the database
            dataset = Dataset(file_name=datafile.name, original_file=datafile)
            dataset.processed_file_pkl = processed_data_pkl 
            dataset.save()

            for col_name, dtype in zip(processed_df.columns, processed_df.dtypes):
                user_friendly_type = get_user_friendly_dtype(dtype)
                dataset.column_types.create(column_name=col_name, original_type=str(dtype), inferred_type=str(dtype), user_modified_type=user_friendly_type)
            return JsonResponse({'processed_data': processed_data_list, 'columns_with_types': columns_with_types})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


@csrf_exempt
def override_data_type(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            column = data.get('column')
            new_type = data.get('new_type')

            # Get the most recent dataset
            dataset = Dataset.objects.order_by('-uploaded_at').first()

            if dataset is None:
                return JsonResponse({'error': 'No dataset available to modify.'}, status=400)

            # Deserialize dataframe from pickle
            processed_df = pickle.loads(dataset.processed_file_pkl)

            # Retrieve column types from the database
            column_types = dataset.column_types.all()
            column_types_dict = {col.column_name: col for col in column_types}

            success, message = override_data(processed_df, column, new_type)

            if success:
                # Update column type in the database
                column_obj = column_types_dict[column]
                column_obj.user_modified_type = new_type
                column_obj.save()

                # Re-serialize and save updated dataframe
                dataset.processed_file_pkl = pickle.dumps(processed_df)
                dataset.save()

                # Update columns_with_types
                columns_with_types = [
                    {'column': col.column_name, 'data_type': col.user_modified_type or col.inferred_type}
                    for col in column_types
                ]

                processed_data_list = serialise_dataframe(processed_df)
                return JsonResponse({
                    'processed_data': processed_data_list,
                    'columns_with_types': columns_with_types,
                    'message': message 
                })
            else:
                return JsonResponse({'error': message}, status=500)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)