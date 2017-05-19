import aws_sg_mngr.api
import aws_sg_mngr.awsSecurityGroup
import json

class MockClient(object):

    def describe_security_groups(self):
        with open('tests/example-security-group.txt', 'r') as testfile:
            security_groups_response = json.load(testfile)

        security_groups_response['ResponseMetadata'] = {}
        security_groups_response['ResponseMetadata']['HTTPStatusCode'] = 200

        return security_groups_response


def test_get_security_groups():
    api = aws_sg_mngr.api.Api('us-east-1')
    api.client = MockClient()

    groups = api.get_security_groups()

    sg = groups.groups[0]
    assert sg is not None
    assert 'Created for Elasticsearch' in sg.description
    assert sg.group_id == 'sg-ebe1ac8f'
    assert sg.group_name == 'Elasticsearch'

    # for rule in sg.egress_rules:
    #     print("- Egress rule: {}".format(str(rule)))
    # for rule in sg.ingress_rules:
    #     print("+ Ingress rule: {}".format(str(rule)))

    assert len(sg.egress_rules) == 1
    assert sg.egress_rules[0].protocol == aws_sg_mngr.awsSecurityGroup.ALL_PROTOCOLS
    assert sg.egress_rules[0].cidr == "0.0.0.0/0"

    assert len(sg.ingress_rules) == 9
    assert sg.ingress_rules[0].protocol == 'tcp'
    assert sg.ingress_rules[0].cidr == "209.6.205.245/32"
    assert sg.ingress_rules[0].from_port == 22
    assert sg.ingress_rules[0].to_port == 22
