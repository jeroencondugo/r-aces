from cdg_service.service.common.base_service import Service
from cdglib.models_client import Organisation
# from cdglib.models_general import User, AssignedPermission
import glob, os
from pprint import pprint


class FileTypeService(Service):
    """ Service for serving file types """

    def create(self, file):
        raise NotImplementedError("Method not implemented!")

    def read(self, extensions=[]):
        """ Return file types """
        file_types = [
            {
                "name": "Excel files",
                "extensions": ["xls", "xlsx"]
            },
            {   "name": "CSV files",
                "extensions": ["csv"]
            }
        ]
        return file_types

    def update(self, file_name, new_file):
        raise NotImplementedError("Method not implemented!")

    def delete(self, file):
        raise NotImplementedError("Method not implemented!")
