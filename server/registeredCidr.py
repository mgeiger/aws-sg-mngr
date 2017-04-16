
class RegisteredCidr(object):
    """ Describes a registered CIDR, which provides the needed information
        to resolve the CIDR in an AWS Security Group
    """

    DO_NOT_EXPIRE=0

    def __init__(self, cidr, description, owner=None, location=None, expiration=DO_NOT_EXPIRE):
        self.cidr = cidr.decode('utf-8')
        self.description = description
        self.location = location
        self.owner = owner
        self.expiration = expiration
    


    def matches(self, other_cidr):
        # other_cidr = other_cidr.decode('utf-8')

        if isinstance(other_cidr, self.cidr.__class__):
            result =  self.cidr == other_cidr
        else:
            result = False

        # print 'comparing {} ({}) to {} ({}):: {}'.format(self.cidr, len(self.cidr), other_cidr, len(other_cidr), result)
        return result

    def __str__(self):
        return "{} - {}".format(self.cidr, self.description)


    def __str__(self):
        result = '{'
        result += ' Description: "{}" '.format(self.description)
        result += ', CIDR: "{}" '.format(self.cidr)
        result += ', Owner: "{}" '.format(self.owner)
        result += ', Expiration: "{}" '.format(self.expiration)
        result += '}'