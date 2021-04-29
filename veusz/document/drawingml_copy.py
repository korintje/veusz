import zipfile
import xml.etree.ElementTree as ET
import os
import io

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
        self.bottom_axis = None
        self.left_axis = None
        self.top_axis = None
        self.right_axis = None
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
            axPos = axis.find(c + "axPos").get("val")
            if axPos == "b":
                self.bottom_axis = Axis(axis, "num")
            elif axPos == "l":
                self.left_axis = Axis(axis, "num")
            elif axPos == "t":
                self.left_axis = Axis(axis, "num")
            elif axPos == "r":
                self.left_axis = Axis(axis, "num")
        for axis in cataxes:
            axPos = axis.find(c + "axPos").get("val")
            if axPos == "b":
                self.bottom_axis = Axis(axis, "text")
            elif axPos == "l":
                self.left_axis = Axis(axis, "text")
            elif axPos == "t":
                self.left_axis = Axis(axis, "text")
            elif axPos == "r":
                self.left_axis = Axis(axis, "text")
        # Set charts
        self.scatterCharts = [ScatterChart(element) for element in plotarea.findall(c + "scatterChart")]
        self.barCharts = [BarChart(element) for element in plotarea.findall(c + "barChart")]


class Axis():

    def __init__(self, element, axistype):
        self.type = axistype
        self.min = None
        self.max = None
        self.parse()

    def parse(self):
        pass


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
        self.x_vals = [float(v.find(c + "v").text) for v in x_wrap.find(c + "numCache").find(c + "pt")]
        self.y_vals = [float(v.find(c + "v").text) for v in y_wrap.find(c + "numCache").find(c + "pt")]
        # self.xRef = self.element.find(c + "xVal").find(c + "numRef").find(c + "f").text
        # self.yRef = self.element.find(c + "yVal").find(c + "numRef").find(c + "f").text
        # xs = self.element.find(c + "xVal").find(c + "numRef").find(c + "numCache").findall(c + "pt")
        # ys = self.element.find(c + "yVal").find(c + "numRef").find(c + "numCache").findall(c + "pt")
        # x_idxs = [int(x.get("idx")) for x in xs]
        # y_idxs = [int(y.get("idx")) for y in ys]
        # self.x_vals = [float(x.find(c + "v").text) for x in xs]
        # self.y_vals = [float(y.find(c + "v").text) for y in ys]
        # self.x_pts = list(zip(*sorted(zip(x_idxs, x_vals))))[1]
        # self.y_pts = list(zip(*sorted(zip(y_idxs, y_vals))))[1]


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
        self.vals = [float(v.find(c + "v").text) for v in val_wrap.find(c + "numCache").find(c + "pt")]


def get_charts(ba: bytearray) -> list:
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
        return charts # list of "Chart" objects


def toMimes(ba: bytearray):

    charts = get_charts(ba)
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

        # Append adding axis commands
        mod_cmd.append("Add('axis', name=u'x', autoadd=False)")
        mod_cmd.append("Add('axis', name=u'y', autoadd=False)")



        x_axis = chart.category_axis
        y_axis = chart.value_axis
        #header.append("graph")
        #graph_title = chart.chart_title.text_frame.text if chart.has_title else "graph1"
        #graph_title = "graph{}".format(str(i+1))
        #header.append("'{}'".format(graph_title))
        # header.append("'/page1/{}'".format(graph_title))



        body.append("To(u'x')")
        if x_axis.axis_title.has_text_frame:
            body.append("Set('label', u'{}')".format(x_axis.axis_title.text_frame.text))
        if x_axis.minimum_scale:
            body.append("Set('min', {})".format(x_axis.minimum_scale))
        if x_axis.maximum_scale:
            body.append("Set('max', {})".format(x_axis.maximum_scale))
        body.append("To('..')")

        body.append("To(u'y')")
        body.append("Set('direction', u'vertical')")
        if y_axis.axis_title.has_text_frame:
            body.append("Set('label', u'{}')".format(y_axis.axis_title.text_frame.text))
        if y_axis.minimum_scale:
            body.append("Set('min', {})".format(y_axis.minimum_scale))
        if y_axis.maximum_scale:
            body.append("Set('max', {})".format(y_axis.maximum_scale))
        body.append("To('..')")

        for j, plot in enumerate(chart.plots):
            for k, series in enumerate(plot.series):
                xDataName = series.name if series.name else "xData"
                xDataName += "_{}{}{}".format(i, j, k)
                yDataName = series.name if series.name else "yData"
                yDataName += "_{}{}{}".format(i, j, k)
                plottype = type(plot)
                if plottype is pptx.chart.plot.XyPlot:
                    body.append("Add('xy', name=u'xy{}', autoadd=False)".format(str(k+1)))
                    body.append("To(u'xy{}')".format(str(k+1)))
                    body.append("Set('xData', '{}')".format(xDataName))
                    body.append("Set('yData', '{}')".format(yDataName))
                    body.append("To('..')")

                    xData, yData = read_xy(series)
                    data_commands.append("ImportString(u'`{}`(numeric)','''".format(xDataName))
                    for datapoint in xData:
                        data_commands.append(str(datapoint))
                    data_commands.append("''')")
                    data_commands.append("ImportString(u'`{}`(numeric)','''".format(yDataName))
                    for datapoint in yData:
                        data_commands.append(str(datapoint))
                    data_commands.append("''')")         
                    
                elif plottype is pptx.chart.plot.BarPlot:
                    print("I see, bar")
                elif plottype is pptx.chart.plot.LinePlot:
                    print("Ah, Line plot")
                else:
                    print("what?")

        header.append(str(len(body)))
        headers += header
        bodies += body

    widget_commands = graph_num + headers + bodies
    widget_savetext = '\n'.join(widget_commands) + '\n' + '\n'.join(body) + '\n'
    data_savetext = '\n'.join(data_commands) + '\n'

    tmpdir.cleanup()

    return widget_savetext, data_savetext