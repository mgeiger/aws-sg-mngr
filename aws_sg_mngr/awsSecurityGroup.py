import logging

ALL_PROTOCOLS = '-1'

class IpRule(object):
    def __init__(self, protocol, cidr):
        self.protocol = protocol
        self.cidr = cidr

class EgressRule(IpRule):

    def __init__(self, protocol, cidr):
        IpRule.__init__(self, protocol, cidr)

    def __str__(self):
        return '{{"Protocol": "{}", "CIDR": "{}"}}' \
            .format(self.protocol, self.cidr)        

class IngressRule(IpRule):

    def __init__(self, protocol, from_port, to_port, cidr):
        IpRule.__init__(self, protocol, cidr)
        self.from_port = from_port
        self.to_port = to_port

    def __str__(self):
        return '{{"Protocol": "{}", "CIDR": "{}", "FromPort": {}, "ToPort": {}}}' \
            .format(self.protocol, self.cidr, self.from_port, self.to_port)        


class AwsSecurityGroups(object):

    def __init__(self, groups):
        self.groups = groups

    @staticmethod
    def from_boto(client):

        result = []
        response = client.describe_security_groups()

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print('Error getting SecurityGroup data from AWS:',)
            print(response['ResponseMetadata'])
            return None
        
        for curr in response['SecurityGroups']:
            group = AwsSecurityGroup.Builder._from_SecurityGroups_item_(curr).build()
            result.append(group)

        return AwsSecurityGroups(result)

    def __str__(self):
        return '[ {} ]'.format(' , '.join(str(x) for x in self.groups))


class AwsSecurityGroup(object):

    class Builder(object):

        def __init__(self):
            self.data = {}
            self.data['IngressRules'] = []
            self.data['EgressRules'] = []

        def build(self):
            # print 'Building AwsSecurityGroup with {}'.format(self.data)
            return AwsSecurityGroup(
                self.data['GroupId'],
                self.data['GroupName'],
                self.data['Description'],
                self.data['IngressRules'],
                self.data['EgressRules'])

        def withGroupId(self, group_id):
            self.data['GroupId'] = group_id

        def withOwnerId(self, owner_id):
            self.data['OwnerId'] = owner_id            

        def withGroupName(self, group_name):
            self.data['GroupName'] = group_name

        def withDescription(self, description):
            self.data['Description'] = description

        def withTags(self, tags):
            self.data['Tags'] = tags

        def withIngressRule(self, protocol, from_port, to_port, cidr):
            new_rule = IngressRule(protocol, from_port, to_port, cidr)
            self.data['IngressRules'].append(new_rule)

        def withEgressRule(self, protocol, from_port, to_port, cidr):
            new_rule = EgressRule(protocol, cidr)
            self.data['EgressRules'].append(new_rule)

        def withRuleList(self, builder_function, ip_permisisons_list):
            """ Helper function which allows the building of ingress & egress rules """
            for curr in ip_permisisons_list:

                from_port = None
                to_port = None
                protocol = curr['IpProtocol']

                try:
                    from_port = curr['FromPort']
                    to_port = curr['ToPort']
                except KeyError:
                    pass

                ranges = curr['IpRanges']
                for curr_cidr in ranges:
                    cidr = curr_cidr['CidrIp']
                    builder_function(protocol, from_port, to_port, cidr)


        @staticmethod
        def _from_SecurityGroups_item_(group):
            """ Creates a builder of a list of groups as returned from
                > aws describe-security-groups
            """

            """
            "GroupName": "launch-wizard-1",
            "VpcId": "vpc-9cc444f8",
            "OwnerId": "105402084108",
            "GroupId": "sg-2bfe3550"
            "Description": "launch-wizard-1 created 2016-05-13T23:35:15.480-04:00",
            "Tags": [
            {
              "Value": "Penguinwrench",
              "Key": "Name"
            }
            ],
            """
            builder = AwsSecurityGroup.Builder()
            builder.withGroupName(group['GroupName'])
            # result['VpcId'] = group['VpcId']
            builder.withOwnerId(group['OwnerId'])
            builder.withGroupId(group['GroupId'])
            builder.withDescription(group['Description'])

            try:
                builder.withTags(group['Tags'])
            except KeyError:
                builder.withTags([])


            egress_list = group['IpPermissionsEgress']
            builder.withRuleList(builder.withEgressRule, egress_list)


            # for curr_egress in egress_list:
            #     from_port = curr_egress['FromPort']
            #     to_port = curr_egress['ToPort']
            #     protocol = curr_egress['IpProtocol']
            #     ranges = curr_egress['IpRanges']
            #     for curr_cidr in ranges:
            #         cidr = curr_cidr['CidrIp']
            #         builder.withEgressRule(protocol, from_port, to_port, cidr)

            # description = curr_egress['Description']
            # tags_list = curr_egress['Tags']

            permissions_list = group['IpPermissions']
            builder.withRuleList(builder.withIngressRule, permissions_list)
            # for curr_permission in permissions_list:
            #     curr_permission['FromPort']
            #     curr_permission['ToPort']
            #     curr_permission['IpProtocol']
            #     ip_ranges = curr_permission['IpRanges']
            #     for curr_range in ip_ranges:
            #         curr_range['CidrIp']
            #     curr_permission[]


            # curr = {}


            # for permission in aws_group['IpPermissions']:
            #     print 'permission: ', permission
            #     base_rule = {}
            #     base_rule['FromPort'] = permission['FromPort']
            #     base_rule['ToPort'] = permission['ToPort']
            #     base_rule['IpProtocol'] = permission['IpProtocol']

            #     for cidr in permission['IpRanges']:
            #         print 'cidr', cidr[u'CidrIp']
            #         rule = base_rule
            #         rule['CidrIp'] = cidr[u'CidrIp']

            #         mngr_group = find_mngr_sg(mngr_sgs, cidr['CidrIp'])
            #         #cidr_info = {}
            #         if mngr_group is not None:
            #             print '!!!!!! matching mngr_group:', mngr_group
            #             rule['Owner'] = mngr_group.owner
            #             rule['Description'] = mngr_group.description
            #             curr['Rules'].append(rule)

            return builder



        # def from_boto(client):
        #     client.describe_security_groups(self, *args, **kwargs)
        #   .. _Protocol Numbers: http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
        #   .. _Security Groups for Your VPC: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_SecurityGroups.html
        #   .. _Amazon EC2 Security Groups: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html


    def __init__(self, group_id, group_name, description, ingress_rules, egress_rules):
        self.group_id = group_id
        self.group_name = group_name
        self.description = description
        self.ingress_rules = ingress_rules
        self.egress_rules = egress_rules

    def __str__(self):
        result = '{'
        result += ' "Description": "{}" '.format(self.description)
        result += ', "GroupId": "{}" '.format(self.group_id)
        result += ', "GroupName": "{}" '.format(self.group_name)
        result += ', "IngressRules": [{}] '.format(__listjoin__(self.ingress_rules))
        result += ', "EgressRules": [{}] '.format(__listjoin__(self.egress_rules))
        result += "}"
        return result


def __listjoin__(the_list):
    return ','.join(str(x) for x in the_list)
