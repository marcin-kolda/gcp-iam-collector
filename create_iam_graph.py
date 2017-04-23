import logging
import sys

from gcp_iam_iterator import GcpIamIterator
from visualisation.graph import Node, Edge
from visualisation import template_renderer

logging.basicConfig(
    format='%(asctime)s %(levelname)-5s %(filename)-12s %(message)s',
    level=logging.DEBUG, stream=sys.stdout)


def get_project_enabled_services(iam_iterator, project_id):
    iterator = iam_iterator.list_enabled_services(project_id)
    services = [v['serviceName'][:-15] for v in iterator if
                v['serviceName'] in ['cloudresourcemanager.googleapis.com',
                                     'appengine.googleapis.com',
                                     'deploymentmanager.googleapis.com',
                                     'servicemanagement.googleapis.com']]
    return services


def create_graph(iam_iterator, projects):
    nodes = {}
    edges = []
    for counter, project in enumerate(projects):
        project_id = project['projectId']
        logging.info("parsing project [{0}] projectId: {1}"
                     .format(counter, project_id))
        project_properties = {k: v for k, v in project.iteritems() if
                              k in ['projectNumber', 'name', 'createTime',
                                    'projectId']}
        services = get_project_enabled_services(iam_iterator, project_id)
        project_properties['enabled_services'] = ", ".join(services)
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
    for counter, project in enumerate(projects):
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
            edges.append(Edge(project_node, sa_node))
    return nodes.values(), edges


def dfs(edges_per_project, start):
    visited_nodes = set()
    stack = [start]
    edges = []
    while stack:
        node = stack.pop()
        if node not in visited_nodes:
            visited_nodes.add(node)
            for edge in edges_per_project[node.id]:
                edges.append(edge)
                if edge.node_to not in visited_nodes:
                    stack.append(edge.node_to)
    return visited_nodes, edges


def render_from_single_node(initial_node, nodes, edges):
    edges_per_project = {}
    for edge in edges:
        project_edges = edges_per_project.get(edge.node_from.id, [])
        project_edges.append(edge)
        edges_per_project[edge.node_from.id] = project_edges
    nodes_dict = {}
    for node in nodes:
        nodes_dict[node.id] = node

    nodes, edges = dfs(edges_per_project, nodes_dict[initial_node])

    template_renderer.render(nodes, edges, 'iam_graph.html')

if __name__ == '__main__':
    iam_iterator = GcpIamIterator(use_cache=False)
    projects = list(iam_iterator.list_projects())
    nodes, edges = create_graph(iam_iterator, projects=projects)

    template_renderer.render(nodes, edges, 'iam_graph_full.html')

