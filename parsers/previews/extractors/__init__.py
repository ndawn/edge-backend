import logging


logger = logging.getLogger()


class ModelExtractor:
    model = None

    field_lookup_pattern = 'get_%s'

    _fields = ()
    _non_null_fields = {}
    _cached_data = {}

    def __init__(self, tree, cache=None):
        self.tree = tree

        if self.model is None:
            raise AttributeError('Extractor instance must have a model class')

        logger.debug('Model class: ' + str(self.model))

        self._field_names = [field.name for field in self.model._meta.fields]
        logger.debug('Field names: ', str(self._field_names))

        if cache is not None:
            for key in cache.keys():
                self.cached_data[key] = cache[key]

        self._populate()

        logger.debug('Extracted data: ' + str(self.fields))

        self._non_null_fields = {k: v for k, v in self._fields if v is not None}

        self._model_instance = self.model(**self._non_null_fields)

    @property
    def fields(self):
        return dict(self._fields)

    @property
    def non_null_fields(self):
        return self._non_null_fields

    @property
    def model_instance(self):
        return self._model_instance

    def _populate(self):
        for field in self._field_names:
            self._fields += (
                (
                    field,
                    getattr(self, self.field_lookup_pattern % field, lambda: None)(),
                ),
            )

    @property
    def cached_data(self):
        return ModelExtractor._cached_data
