type_properties = {
    'project': {
        'name': 'GCP Project',
        'font_code': '\uf1ad',
        'size': 70,
        'color': '#000066'
    },
    'serviceAccount': {
        'name': 'Service Account',
        'font_code': '\uf084',
        'size': 50,
        'color': '#000066'
    },
    'unknown': {
        'name': 'Unknown',
        'font_code': '\uf128',
        'size': 50,
        'color': '#FF0000'
    }
}


class Node:
    def __init__(self, node_type, id, name, title=None, color_group=None,
                 properties=None):
        if not id:
            raise ValueError("Node id must be not null")
        self.node_type = node_type
        self.id = id
        self.name = name
        self.title = title
        self.color_group = color_group
        self.properties = properties

    def get_color(self):
        if self.color_group:
            return self.color_group
        return type_properties[self.node_type]['color']

    def get_font_code(self):
        return type_properties[self.node_type]['font_code']

    def get_size(self):
        return type_properties[self.node_type]['size']

    def get_type_name(self):
        return type_properties[self.node_type]['name']

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return 'a %s called %s' % (self.node_type, self.name)

    def __unicode__(self):
        return unicode(self.__str__())


class Edge:
    def __init__(self, node_from, node_to, label=None, title=None, role=None):
        self.node_from = node_from
        self.node_to = node_to
        self.label = label
        self.title = title if title else role
        self.role = role
