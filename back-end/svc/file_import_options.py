from sqlalchemy.orm import make_transient

from cdg_service.errors import InvalidParameter, NotFound
from cdg_service.schemes.file_imports import FileImporterOptionsUpdateSchema, FileImporterOptionsCreateSchema
from cdg_service.service.common.base_service import Service
from cdglib import get_all_subclasses
from cdglib.models_client import FileImporterOptions, FileImporter
from cdglib.models_client.file_imports import FileImporterExcelOptions, FileImporterCsvOptions, FileImporterDsoOptions, \
    FileImporterMbusOptions, FileImporterMaxeeOptions


class FileImportOptionsService(Service):

    # Create a file_importer
    def create(self, json_data):
        # Bug if no id is given.
        type = None
        if '_type' in json_data:
            json_data['type'] = json_data['_type']
        if 'type' in json_data:
            type = json_data['type']
        if not isinstance(type, str):
            raise InvalidParameter("FileImporterType is not supported, must be string with class name!")
        if type is None or type not in get_all_subclasses(FileImporterOptions, format="name"):
            raise InvalidParameter("FileImporterType is not supported!")
        if 'id' in json_data and self.session.query(FileImporterOptions).get(json_data['id']) is not None:
            raise InvalidParameter('FileImporterOptions id already exists!')
        if "importer_id" not in json_data:
            raise InvalidParameter('FileImporter id must be defined!')
        if not isinstance(json_data['importer_id'], int):
            raise InvalidParameter("FileImporter id is not supported, must be integer!")
        file_importer = self.session.query(FileImporter).get(json_data['importer_id'])
        if file_importer is None:
            raise InvalidParameter(f"FileImporter with id {json_data['importer_id']} does not exist!")
        if not file_importer.type == type.replace("Options", ""):
            raise InvalidParameter("Type of file importer options and FileImporter are not the same")
        importer_options = self._new_file_importer_options(type)() if self._new_file_importer_options(type) else None
        if not importer_options:
            raise InvalidParameter(f"FileImporterOptions type ({type}) is not supported!")
        serializer = FileImporterOptionsCreateSchema()  # _file_importer_options_schema(type)
        res = serializer.load(json_data, session=self.session, instance=importer_options, partial=True)
        if res.errors:
            raise InvalidParameter(f"Validation errors: {res.errors}")
        importer_options = res.data
        self.session.add(importer_options)

        return importer_options

    # If id is defined, will ignore importer_id
    def read(self, id=None, importer_id=None):
        if id is None and importer_id is None:
            return self.session.query(FileImporterOptions).all()
        if id is not None:
            importer_options = self.session.query(FileImporterOptions).get(id)
            if importer_options is None:
                raise InvalidParameter(f'No options found with that id')
            return importer_options
        if importer_id is not None:
            importer_options = self.session.query(FileImporterOptions).filter(
                FileImporterOptions.importer_id == importer_id).all()
            if importer_options is None:
                raise InvalidParameter(f'No options found with that importer_id')
            return importer_options

    # Update a file importer given a full file_importer
    # Giving type is required due to inheritance!
    def update(self, id, json_data):
        # Bug if no id is given.
        type = None
        if '_type' in json_data:
            json_data['type'] = json_data['_type']
        if 'type' in json_data:
            type = json_data['type']
        if not isinstance(type, str):
            raise InvalidParameter("FileImporterOptionsType is not supported, must be string with class name!")
        if type is None or type not in get_all_subclasses(FileImporterOptions, format="name"):
            raise InvalidParameter(f"FileImporterOptionsType ({type})is not supported!")
        file_importer_options = self.session.query(FileImporterOptions).get(id)
        if file_importer_options is None:
            raise InvalidParameter('FileImporterOptions id does not exist')
        json_data['id'] = id
        serializer = FileImporterOptionsUpdateSchema()  # _file_importer_options_schema(json_data['type'])
        if not file_importer_options.type == type:
            raise InvalidParameter("Changing type of FileImporterOptions is not allowed.")
        if not file_importer_options.importer_id == json_data['importer_id']:
            raise NotFound('Not allowed to change importer options id')
        res = serializer.load(json_data, session=self.session, instance=file_importer_options)
        if res.errors:
            raise InvalidParameter(f"Validation errors: {res.errors}")

        self.session.commit()

        # Update the scheduler
        from cdgworkers.scheduler import Scheduler
        task = Scheduler.load_task("cdgworkers.imports.importer_worker.remove_and_update_scheduler")

        return file_importer_options

    # Delete a file importer given a id
    def delete(self, id):
        if not isinstance(id, int):
            raise InvalidParameter("FileImporterOptions id is not supported, must be integer!")
        file_importer_options = self.session.query(FileImporterOptions).get(id)
        if file_importer_options is None:
            raise InvalidParameter(f"FileImporterOptions {id} does not exist!")
        self.session.delete(file_importer_options)
        return file_importer_options

    def copy(self, id):
        if not isinstance(id, int):
            raise InvalidParameter("FileImporter_options id is not supported, must be integer!")
        subclasses = sub_classes_options = get_all_subclasses(FileImporterOptions)
        file_importer_options = None
        for subclass in subclasses:
            if subclass.__name__ == 'CsvExcelCommonOptions':
                continue
            file_importer_options = self.session.query(subclass).get(id)
            if file_importer_options is not None:
                break
        if file_importer_options is None:
            raise InvalidParameter("FileImporter_options id does not exist!")
        self.session.expunge(file_importer_options)
        make_transient(file_importer_options)
        file_importer_options.id = None
        self.session.add(file_importer_options)
        self.session.flush()
        return file_importer_options

    # Search for active file importers between given dates
    def search(self, param):
        raise NotImplementedError

    @classmethod
    def schedule_async(cls, task_id: str, *args):
        """ Schedule task with given id to be scheduled for async execution. task_id is in form of: reports.update.update_all_reports """
        from cdgworkers.scheduler import Scheduler

        task = Scheduler.load_task(task_id)
        return task.delay(*args)

    @classmethod
    def _new_file_importer_options(cls, type):
        str2type = {
            "FileImporterExcelOptions": FileImporterExcelOptions,
            "FileImporterCsvOptions": FileImporterCsvOptions,
            "FileImporterDsoOptions": FileImporterDsoOptions,
            "FileImporterMbusOptions": FileImporterMbusOptions,
            "FileImporterMaxeeOptions": FileImporterMaxeeOptions,
        }
        return str2type.get(type)
