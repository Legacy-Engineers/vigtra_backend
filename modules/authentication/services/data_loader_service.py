from .. import MODULE_BASE_DIR
import os
from modules.core.utils import get_data_from_file
from django.contrib.auth.models import Group


class DataLoaderService:

    def load_groups(self):
        json_file = os.path.join(MODULE_BASE_DIR, 'model_data_files/groups.json')
        json_data = get_data_from_file(file_path=json_file, file_type='json')

        results = []

        if json_data:
            group_data = json_data.get('data')

            for group in group_data:
                group_name = group.get('name')
                group_permissions = group.get('permissions')

                existing_group, created_group = Group.objects.get_or_create(name__icontains=group_name)

                if created_group:
                    created_group.permissions.set(group_permissions)
                    created_group.save()

                    result_data = {
                        "success": True,
                        "message": f"Group '{group_name}' created successfully.",
                        "data": created_group.__dict__
                    }
                else:
                    result_data = {
                        "success": False,
                        "message": f"Group '{group_name}' already exists.",
                        "data": existing_group.__dict__
                    }

                results.append(result_data)