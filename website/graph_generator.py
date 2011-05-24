# -*- coding: utf-8 -*-
"""
    Generator of graphs using RGraph
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    RGraph is the library we use to generate the JavaScript graphs.
"""

from string import Template
import datetime

class GraphGenerator(object):
    """
        The script to generate is defined here as a template and we
        insert the data we want to display. 
    """
    
    empty = 'null'
    
    template = Template("""
window.onload = function ()
    {
        graph = new RGraph.Line('$name' $lines);
        graph.Set('chart.tooltips', $tooltips);
        graph.Set('chart.gutter', 70);
        graph.Set('chart.tickmarks', 'circle');
        graph.Set('chart.shadow', 'true');
        graph.Set('chart.background.grid.autofit', true);
        graph.Set('chart.labels', $labels);
        graph.Set('chart.text.angle', 45);
        graph.Set('chart.linewidth', 1);
        graph.Set('chart.title', '$title');
        graph.Set('chart.title.xaxis', 'Date');
        graph.Set('chart.title.yaxis', 'Rank');
        graph.Set('chart.ymin', $min);
        graph.Set('chart.ymax', $max);
        graph.Set('chart.scale.decimals', 5);
        graph.Set('chart.key', $keys);
        graph.Set('chart.contextmenu', [['Zoom entire graph', RGraph.Zoom]]);
        graph.Draw();
    }
""")
    
    def __init__(self, name):
        self.first_date = None
        self.last_date = None
        self.lines = []
        self.keys = []
        self.labels = None
        self.title = None
        self.name = name

    def add_line(self, line, key, first_date, last_date):
        """
            Add all the data needed to display a line on the graph
        """
        self.set_labels(first_date, last_date)
        self.lines.append(self.line_values(line))
        self.keys.append(key)
    
    def line_values(self, line):
        """
            Prepare the components of a line
        """
        list = []
        for label in self.labels:
            rank = line.get(label, None)
            if rank > 0:
                list.append(1 + rank)
            else:
                list.append(self.empty)
        return list

    def repr_list(self, list):
        """
            Prepare a string representation of the liste RGrah-friendly
        """
        to_return = '['
        for l in list:
            if len(to_return) > 1:
                to_return += ', '
            to_return += str(l)
        to_return += ']'
        return to_return
    
    # xaxis
    def set_labels(self, first_date, last_date):
        """
            Prepare the label, on the X axis
        """
        if self.first_date is None or self.last_date is None or first_date < self.first_date or last_date > self.last_date:
            self.first_date = first_date
            self.last_date = last_date
            self.labels = []
            current = first_date
            while current <= last_date:
                self.labels.append(current.strftime("%Y-%m-%d"))
                current += datetime.timedelta(days=1)
    
    def set_title(self, title):
        """
            Set the title of the schema
        """
        self.title = title

    def make_js(self):
        """
            Populate the template and build the js
        """
        form_lines = ''
        tooltips = []
        real_max = 0
        for line in self.lines:
            form_lines += ', ' + self.repr_list(line)
            tooltips += line
            line = filter (lambda a: a != self.empty, line)
            if len(line) > 0:
                real_max = max(real_max, max(line))
        form_keys = str(self.keys)
        real_min = 1.0
        self.js = self.template.substitute( name = self.name, lines = form_lines, tooltips = self.repr_list(tooltips), labels = str(self.labels), title = self.title, min = real_min, max = real_max, keys = str(self.keys) )

if __name__ == "__main__":
    g = GraphGenerator('plop')
    g.add_line([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'test')
    g.add_line([10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 'test 2')
    g.set_labels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'])
    g.set_title('Test perso')
    g.make_js()
    g = GraphGenerator('plop')
    g.add_line([10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 'test 3')
    print g.js
