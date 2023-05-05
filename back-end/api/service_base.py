#  Copyright (c) 2015-2020 Condugo bvba

import abc

class ServiceBase(object, metaclass=abc.ABCMeta):
    """Abstract base class for CRUD services"""

    @abc.abstractmethod
    def get_object(self, client, id):
        """Get single object from client filtered by id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_objects(self, client, filter=None):
        """Get all objects from client"""
        raise NotImplementedError

    @abc.abstractmethod
    def create_object(self, client, json_data):
        """Create single object for client based on json_data"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_object(self, client, json_data):
        """Update single object from client filtered by id and updated by json_data"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_object(self, client, id):
        """Delete single object from client filtered by id"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_objects(self, client, id_list):
        """Delete multiple objects from client filtered by id_list"""
        raise NotImplementedError
