import pickle
from datetime import datetime

from motorengine import *  # NOQA
from motorengine import signals


class PickleEmbedded(EmbeddedDocument):
    date = DateTimeField(default=datetime.now)


class PickleTest(Document):
    number = IntField()
    string = StringField(choices=(('One', '1'), ('Two', '2')))
    embedded = EmbeddedDocumentField(PickleEmbedded)
    lists = ListField(StringField())
    photo = FileField()


class PickleSignalsTest(Document):
    number = IntField()
    string = StringField(choices=(('One', '1'), ('Two', '2')))
    embedded = EmbeddedDocumentField(PickleEmbedded)
    lists = ListField(StringField())

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        pickled = pickle.dumps(document)
        assert pickled is not None

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        pickled = pickle.dumps(document)
        assert pickled is not None

signals.post_save.connect(PickleSignalsTest.post_save, sender=PickleSignalsTest)
signals.post_delete.connect(PickleSignalsTest.post_delete, sender=PickleSignalsTest)


class Mixin(object):
    name = StringField()


class Base(Document):
    meta = {'allow_inheritance': True}
