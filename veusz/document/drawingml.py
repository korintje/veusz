import os
import io
import zipfile
import xml.etree.ElementTree as ET

Override = r"{http://schemas.openxmlformats.org/package/2006/content-types}Override"
ChartType = r"application/vnd.openxmlformats-officedocument.drawingml.chart+xml"
c = r"{http://schemas.openxmlformats.org/drawingml/2006/chart}"

class ChartFile():

    def __init__(self, xmltext):
        self.xmltext = xmltext
        self.parse()
    
    def parse(self):
        tree = ET.parse(self.xmltext)
        root = tree.getroot()
        self.chart = Chart(root.find(c + "chart"))


class Chart():

    def __init__(self, element):
        self.element = element
        self.title = "graph"
        self.axes = []
        self.scatterCharts = []
        self.barCharts = []
        self.parse()
    
    def parse(self):
        # Set chart title
        title_words = self.element.find(c + "title").find(c + "tx").find(c + "rich").find(c + "p").findall(c + "r")
        self.title = "".join([word.find(c + "t").text for word in title_words]) 
        # Set axes
        plotarea = self.element.find(c + "plotArea")
        valaxes = plotarea.findall(c + "valAx")
        cataxes = plotarea.findall(c + "catAx")
        for axis in valaxes:
            self.axes.append(Axis(axis, "num"))
        for axis in cataxes:
            self.axes.append(Axis(axis, "text"))
        # Set charts
        self.scatterCharts = [ScatterChart(element) for element in plotarea.findall(c + "scatterChart")]
        self.barCharts = [BarChart(element) for element in plotarea.findall(c + "barChart")]


class Axis():

    def __init__(self, element, axistype):
        self.element = element
        self.type = axistype
        self.axPos = "" # "b": bottom, "l": left, "t": top, "r": right
        self.label = ""
        self.min = None
        self.max = None
        self.majorUnit = None
        self.minorUnit = None
        self.majorTickMark = None
        self.minorTickMark = None
        self.parse()

    def parse(self):
        if self.element.find(c + "axPos"):
            self.axPos = self.element.find(c + "axPos").get("val")
        if self.element.find(c + "title"):
            label_words = self.element.find(c + "title").find(c + "tx").find(c + "rich").find(c + "p").findall(c + "r")
            self.label = "".join([word.find(c + "t").text for word in label_words]) 
        scaling = self.element.find(c + "scaling")
        axis_min = scaling.find(c + "min")
        if axis_min:
            self.min = axis_min.get("val")
        axis_max = scaling.find(c + "max")
        if axis_max:
            self.max = axis_max.get("val")
        majorUnit = self.element.majorUnit
        if majorUnit:
            self.majorUnit = majorUnit.get("val")
        minorUnit = self.element.minorUnit
        if minorUnit:
            self.minorUnit = minorUnit.get("val")


class ScatterChart():

    def __init__(self, element):
        self.element = element
        self.parse()

    def parse(self):
        self.serieses = [xySeries(element) for element in self.element.findall(c + "ser")]


class BarChart():

    def __init__(self, element):
        self.element = element
        self.parse()

    def parse(self):
        self.serieses = [cvSeries(element) for element in self.element.findall(c + "ser")]


class xySeries():

    def __init__(self, element):
        self.element = element
        self.xRef = ""
        self.yRef = ""
        self.x_vals = []
        self.y_vals = []
        self.parse()
    
    def parse(self):
        x_wrap = self.element.find(c + "xVal").find(c + "numRef")
        y_wrap = self.element.find(c + "yVal").find(c + "numRef")
        self.xRef = x_wrap.find(c + "f").text
        self.yRef = y_wrap.find(c + "f").text
        self.x_vals = [v.find(c + "v").text for v in x_wrap.find(c + "numCache").find(c + "pt")]
        self.y_vals = [v.find(c + "v").text for v in y_wrap.find(c + "numCache").find(c + "pt")]


class cvSeries():

    def __init__(self, element):
        self.element = element
        self.catRef = ""
        self.valRef = ""
        self.cats = []
        self.vals = []
        self.parse()
    
    def parse(self):
        cat_wrap = self.element.find(c + "cat").find(c + "numRef")
        val_wrap = self.element.find(c + "val").find(c + "numRef")
        self.catRef = cat_wrap.find(c + "f").text
        self.valRef = val_wrap.find(c + "f").text
        self.cats = [v.find(c + "v").text for v in cat_wrap.find(c + "numCache").find(c + "pt")]
        self.vals = [v.find(c + "v").text for v in val_wrap.find(c + "numCache").find(c + "pt")]


def getCharts(ba: bytearray) -> list:
    # Get DrawingML object from clipboard
    stream = io.BytesIO(ba)
    with zipfile.ZipFile(stream, "r") as z:
        with z.open("[Content_Types].xml") as f:
            tree = ET.fromstring(f.read())
        part_names = []
        for link in tree.findall(Override):
            content_type = link.attrib["ContentType"]
            if content_type == ChartType:
                part_name = link.attrib["PartName"]
                part_names.append(part_name)
        charts = []
        for part_name in part_names:
            with io.TextIOWrapper(z.open(part_name.strip("/"), "r")) as f: 
                xmltext = f.read()
                chartfile = ChartFile(xmltext)
                charts.append(chartfile.chart)        
        return charts


def toMimes(ba: bytearray):

    charts = getCharts(ba)
    data_cmds = []
    gen_cmds = []
    mod_cmds = []
    graph_num = [str(len(charts))]
    for i, chart in enumerate(charts):

        # Command lists
        gen_cmd = ["graph"]
        mod_cmd = []

        # Append graph title commands
        graph_title = chart.title + str(i+1)
        gen_cmd.append("'{}'".format(graph_title))
        gen_cmd.append("'/page1/{}'".format(graph_title))

        # Append set_axis commands
        for axis in chart.axes:
            names = {"b": "x1", "l": "y1", "t": "x2", "r": "y2"}
            directions = {"b": "horizontal", "l": "vertical", "t": "horizontal", "r": "vertical"}
            positions = {"b": "0.0", "l": "0.0", "t": "1.0", "r": "1.0"}
            pos = axis.axPos
            mod_cmd.append("Add('axis', name=u'{}', autoadd=False)".format(names[pos]))
            mod_cmd.append("To(u'x')")
            mod_cmd.append("Set('direction', u'{}')".format(directions[pos]))
            mod_cmd.append("Set('otherPosition', {})".format(positions[pos]))
            if axis.label:
                mod_cmd.append("Set('label', u'{}')".format(axis.label))
            if axis.min:
                mod_cmd.append("Set('min', {})".format(axis.min))
            if axis.max:
                mod_cmd.append("Set('max', {})".format(axis.max))
            mod_cmd.append("To('..')")

        # Append set_data commands
        for j, plot in enumerate(chart.scatterCharts):
            for k, series in enumerate(plot.serieses):
                xDataName = series.xRef if series.xRef else "x"
                xDataName += "_{}{}{}".format(i, j, k)
                yDataName = series.yRef if series.yRef else "y"
                yDataName += "_{}{}{}".format(i, j, k)
                mod_cmd.append("Add('xy', name=u'xy{}', autoadd=False)".format(str(k+1)))
                mod_cmd.append("To(u'xy{}')".format(str(k+1)))
                mod_cmd.append("Set('xData', '{}')".format(xDataName))
                mod_cmd.append("Set('yData', '{}')".format(yDataName))
                mod_cmd.append("To('..')")
                data_cmds.append("ImportString(u'`{}`(numeric)','''".format(xDataName))
                for x_val in series.x_vals:
                    data_cmds.append(x_val)
                data_cmds.append("''')")
                data_cmds.append("ImportString(u'`{}`(numeric)','''".format(yDataName))
                for y_val in series.y_vals:
                    data_cmds.append(y_val)
                data_cmds.append("''')")         

        gen_cmd.append(str(len(mod_cmd)))
        gen_cmds += gen_cmd
        mod_cmds += mod_cmd

    widget_commands = graph_num + gen_cmds + mod_cmds
    widget_savetext = '\n'.join(widget_commands) + '\n'
    data_savetext = '\n'.join(data_cmds) + '\n'

    return widget_savetext, data_savetext