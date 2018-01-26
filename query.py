import models as db


class query(object):
    """
    query Class:

    A class to do different queries to the database
    """

    def __init__(self):
        """"
        Default Constructor
        There are no parameters, default is here as there has to be code in the constructor
        """

    def test(self):

        data = db.user.select(db.user.first_name).where(db.user.user_id == 1).tuples()
        data = list(data)[0][0]
        return data
