import fnmatch
import os

from marshmallow import Schema

from cdg_service.service.common.base_service import Service
from cdg_service.errors import InvalidParameter
from cdg_service.schemes.file_imports import FileImporterGlobSchema
from cdglib import StorageFactory, StorageProvider
from cdglib.models_client import FileImporterGlob, FileImporter, Organisation


class FileImportGlobsService(Service):

    # Create an importer_glob, thows error if:
    # * file_importer id not defined
    # * file_importer id not an int
    # * file_importer id does not exist
    def create(self, json_data):
        importer_glob = FileImporterGlob()
        serializer = FileImporterGlobSchema()
        res = serializer.load(json_data, session=self.session, instance=importer_glob, partial=True)
        importer_glob = res.data
        if 'id' in json_data:
            json_data.pop('id')
        if 'importer_id' not in json_data:
            raise InvalidParameter('FileImporter id needs to be defined!')
        if not isinstance(json_data['importer_id'], int):
            raise InvalidParameter('importer_id needs to be an int!')
        if self.session.query(FileImporter).get(json_data['importer_id']) is None:
            raise InvalidParameter(f"FileImporter with id {json_data['importer_id']} does not exist!")
        self.session.add(importer_glob)
        self.session.commit()
        return importer_glob

    # If id is defined, will ignore importer_id
    def read(self, id= None, importer_id=None):
        if id is None and importer_id is None:
            return self.session.query(FileImporterGlob).all()
        if id is not None:
            importer_globs = self.session.query(FileImporterGlob).get(id)
            if importer_globs is None:
                raise InvalidParameter(f'No globs found with that id')
            return importer_globs
        if importer_id is not None:
            importer_globs = self.session.query(FileImporterGlob).filter(
                FileImporterGlob.importer_id == importer_id).all()
            if importer_globs is None:
                raise InvalidParameter(f'No globs found with that importer_id')
            return importer_globs

    #Update a importer_glob, throws error if:
    # * id is not int
    # * id is not specified
    # * importer_id does not exist
    # * file_importer id not specified
    def update(self, id, json_data):
        json_data = json_data['glob']
        if 'importer_id' in json_data and not isinstance(json_data['importer_id'], int):
            raise InvalidParameter('importer_id needs to be an int!')
        importer_glob = self.session.query(FileImporterGlob).get(id)
        if importer_glob is None:
            raise InvalidParameter('ImporterGlob with that id does not exist!')
        serializer = FileImporterGlobSchema()
        if 'importer_id' in json_data and self.session.query(FileImporter).get(json_data['importer_id']) is None:
            raise InvalidParameter(f"FileImporter with id {json_data['importer_id']} does not exist!")
        json_data['id'] = id
        res = serializer.load(json_data, session=self.session, instance=importer_glob, partial=True)
        if res.errors:
            raise InvalidParameter(f'Validation errors: {res.errors}')
        importer_glob = res.data
        return importer_glob

    # Delete on glob id, if importer_glob with id does not exists, throws error
    def delete(self, id):
        if not isinstance(id, int):
            raise InvalidParameter("FileImporterGlob id is not supported, must be integer!")
        importer_glob= self.session.query(FileImporterGlob).get(id)
        if importer_glob is None:
            raise InvalidParameter("FileImporterGlob id does not exist!")
        self.session.delete(importer_glob)
        self.session.commit()
        return importer_glob


    def test(self, json_data):

        if "globs" not in json_data:
            raise InvalidParameter("Payload does not contain globs")
        storage = StorageFactory().create(StorageProvider.AZURE)
        client_id = self.session.query(Organisation).first().client_id()
        bucket_name = f"{client_id}-import"
        matched = []
        not_matched = []
        for file in storage.list_blobs(bucket_name):
            for rule in json_data["globs"]:
                if fnmatch.fnmatch(file.name, rule):
                    matched.append(file.name)
                else:
                    not_matched.append(file.name)
        result = {
            "matched": matched,
            "missed": not_matched,
        }
        return result
