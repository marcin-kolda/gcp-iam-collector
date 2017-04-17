import logging

from gcp_iam_iterator import GcpIamIterator
from visualisation.graph import Node, Edge
from visualisation import template_renderer


def create_project_nodes(iam_iterator):
    nodes = []
    for counter, project in enumerate(iam_iterator.list_projects()):
        project_id = project['projectId']
        logging.info("parsing project [{0}] projectId: {1}"
                     .format(counter, project_id))
        properties = {k: v for k, v in project.iteritems() if
                      'projectNumber' in k or 'name' in k or 'createTime' in k}
        node = Node("project", "p:" + project_id, project_id,
                    properties=properties)
        nodes.append(node)
    return nodes


def create_service_account_nodes(iam_iterator):
    nodes = {}
    edges = []
    for counter, project in enumerate(iam_iterator.list_projects()):
        project_id = project['projectId']
        logging.info("parsing project [{0}] projectId: {1}"
                     .format(counter, project_id))
        project_properties = {k: v for k, v in project.iteritems() if
                              k in ['projectNumber', 'name', 'createTime',
                                    'projectId']}
        project_node = Node("project", "p:" + project_id, project_id,
                            properties=project_properties)
        nodes[project_node.id] = project_node
        for binding in iam_iterator.list_project_iam(project_id):
            role = binding['role']
            for member in binding['members']:
                member_type = member.split(":")[0]
                member_name = member.split(":")[1]
                if member_type == 'serviceAccount':
                    sa_node = Node("serviceAccount", "sa:" + member_name,
                                   member_name,
                                   properties={'email': member_name})
                    edges.append(Edge(sa_node, project_node, role=role))
                    nodes[sa_node.id] = sa_node
    for counter, project in enumerate(iam_iterator.list_projects()):
        project_id = project['projectId']
        project_properties = {k: v for k, v in project.iteritems() if
                              k in ['projectNumber', 'name', 'createTime']}
        project_node = Node("project", "p:" + project_id, project_id,
                            properties=project_properties)
        for sa in iam_iterator.list_service_accounts(project_id):
            email = sa['email']
            sa_id = "sa:" + email
            if sa_id not in nodes:
                continue
            sa_properties = {k: v for k, v in sa.iteritems() if
                             k in ['oauth2ClientId', 'displayName', 'projectId',
                                   'uniqueId', 'email']}
            sa_node = Node("serviceAccount", sa_id, email,
                           properties=sa_properties)
            nodes[sa_node.id] = sa_node
            edges.append(Edge(sa_node, project_node))
    return nodes.values(), edges


if __name__ == '__main__':
    nodes, edges = create_service_account_nodes(GcpIamIterator())

    template_renderer.render(nodes, edges, 'iam_graph.html')
