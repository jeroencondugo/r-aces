from logging import getLogger

from sqlalchemy.orm import make_transient, selectinload

from cdg_service.errors import NotFound, InvalidParameter
from cdg_service.schemes.file_imports import FileImporterCreateSchema, \
    FileImporterUpdateSchema
from cdg_service.service.common.base_service import Service
from cdglib import get_all_subclasses
from cdglib.models_client import FileImporter, FileImporterExcel, FileImporterDso, FileImporterMbus, \
    FileImporterCsv, FileImporterOptions, FileImporterGlob
from cdglib.models_client.file_imports import FileImporterCsvOptions, FileImporterMaxee
from cdglib.models_general import Client
from cdglib import get_all_subclasses

logger = getLogger("cdgsvc-file_imports")


class FileImportsService(Service):

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
        if type is None or type not in get_all_subclasses(FileImporter, format="name"):
            raise InvalidParameter("FileImporterType is not supported!")
        if 'id' in json_data and self.session.query(FileImporter).get(json_data['id']) is not None:
            raise InvalidParameter('FileImporter id already exists!')

        importer = self._new_file_importer(type)()
        serializer = FileImporterCreateSchema()
        res = serializer.load(json_data, session=self.session, instance=importer)
        if res.errors:
            raise InvalidParameter(f'Validation errors: {res.errors}')
        importer = res.data
        self.session.add(importer)
        self.session.commit()
        # Update the scheduler
        try:
            self.schedule_async("imports.importer_worker.remove_and_update_scheduler", importer.id)
        except:
            logger.warn("Could not update the scheduler on update. Are the workers running?")
        return importer

    # Read all file importers
    def read(self):
        options_subclasses = get_all_subclasses(FileImporterOptions)
        return self.session.query(FileImporter).options(
            selectinload(FileImporter.globs),
            selectinload(FileImporter.options)
        ).all()


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
            raise InvalidParameter("FileImporterType is not supported, must be string with class name!")
        if type is None or type not in get_all_subclasses(FileImporter, format="name"):
            raise InvalidParameter("FileImporterType is not supported!")
        file_importer = self.session.query(FileImporter).get(id)
        if file_importer is None:
            raise InvalidParameter('FileImporter id does not exist')
        json_data['id'] = id
        serializer = FileImporterUpdateSchema()
        # if not file_importer.type == type:
        #     raise InvalidParameter("Changing type of FileImporter is not allowed.")
        if not file_importer:
            raise NotFound('No such file importer found')

        res = serializer.load(json_data, session=self.session, instance=file_importer, partial=True)
        if res.errors:
            raise InvalidParameter(f'Validation errors: {res.errors}')
        self.session.commit()

        # Update the scheduler
        try:
            self.schedule_async("imports.importer_worker.remove_and_update_scheduler", file_importer.id)
        except:
            logger.warn("Could not update the scheduler on update. Are the workers running?")
        return file_importer

    # Delete a file importer given a id
    def delete(self, id):
        if not isinstance(id, int):
            raise InvalidParameter("FileImporter id is not supported, must be integer!")
        file_importer = self.session.query(FileImporter).get(id)
        if file_importer is None:
            raise InvalidParameter("FileImporter id does not exist!")
        self.session.delete(file_importer)
        file_importer_id = file_importer.id
        # Remove redbeat schedule task for importer
        try:
            self.schedule_async("imports.importer_worker.remove_scheduler", file_importer_id)
        except:
            logger.warn("Could not remove the scheduler on delete. Are the workers running?")
        return file_importer

    def deep_copy(self, id):
        if not isinstance(id, int):
            raise InvalidParameter("FileImporter id is not supported, must be integer!")
        subclasses = sub_classes_options = get_all_subclasses(FileImporter)
        file_importer = None
        for subclass in subclasses:
            if subclass.__name__ == 'FileImporterCsvExcelCommon':
                continue
            file_importer = self.session.query(subclass).get(id)
            if file_importer is not None:
                break
        if file_importer is None:
            raise InvalidParameter("FileImporter id does not exist!")
        self.session.expunge(file_importer)
        make_transient(file_importer)
        file_importer.id = None
        self.session.add(file_importer)
        self.session.flush()
        new_importer_id = file_importer.id
        for glob in self.session.query(FileImporterGlob).filter(FileImporterGlob.importer_id == id).all():
            self.session.expunge(glob)
            make_transient(glob)
            glob.id = None
            glob.importer_id = new_importer_id
            self.session.add(glob)
        subclasses = sub_classes_options = get_all_subclasses(FileImporterOptions)
        for subclass in subclasses:
            if subclass.__name__ == "CsvExcelCommonOptions":
                continue
            for options in self.session.query(subclass).filter(subclass.importer_id == id).all():
                self.session.expunge(options)
                make_transient(options)
                options.id = None
                options.importer_id = new_importer_id
                self.session.add(options)

        self.session.commit()
        # Update the scheduler
        try:
            self.schedule_async("imports.importer_worker.remove_and_update_scheduler", new_importer_id)
        except:
            logger.warn("Could not update the scheduler on update. Are the workers running?")
        return file_importer

    def run_importer(self, id):
        from cdgworkers.scheduler import Scheduler
        task = Scheduler.load_task("cdgworkers.imports.importer_worker.process_imported_files")
        try:
            task.delay(self.session.query(Client).first().schema, id)
        except:
            logger.info("Could not run importer with id ", id, " something went wrong.")
            raise Exception('Could not run importer. Something went wrong!')

    @classmethod
    def _new_file_importer(cls, type):
        str2type = {
            "FileImporterExcel": FileImporterExcel,
            "FileImporterCsv": FileImporterCsv,
            "FileImporterDso": FileImporterDso,
            "FileImporterMbus": FileImporterMbus,
            "FileImporterMaxee": FileImporterMaxee,
        }
        return str2type.get(type)


