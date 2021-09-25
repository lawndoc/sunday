from mongoengine import Document, EmbeddedDocument, IntField, StringField, DateField, ListField, EmbeddedDocumentField


class Result(EmbeddedDocument):
    name = StringField(required=True)
    school = StringField(required=True)
    meet = StringField(required=True)
    time = StringField(required=True)


class Meet(Document):
    name = StringField(required=True)
    date = DateField(required=True)
    location = StringField()
    boysResults = ListField(EmbeddedDocumentField(Result))
    girlsResults = ListField(EmbeddedDocumentField(Result))


class Athlete(EmbeddedDocument):
    gender = StringField(required=True)
    name = StringField(required=True)
    school = StringField(required=True)
    year = IntField()
    meets = ListField(EmbeddedDocumentField(Result))


class School(Document):
    name = StringField(required=True)
    classSize = StringField(required=True)
    boys = ListField(EmbeddedDocumentField(Athlete))
    girls = ListField(EmbeddedDocumentField(Athlete))
