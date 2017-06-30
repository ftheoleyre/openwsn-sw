import os
from DataBase import DataBase

class Graphs(object):

    def __init__(self, expid):
        self.expid = expid
        self.dbo = DataBase(self.expid)

    def pdr(self):
        self.dbo.cur.execute("SELECT * FROM PDR WHERE expid={}".format(self.expid))
        self.dbo.db.commit()
        res = self.dbo.cur.fetchall()

        f = open('./openvisualizer/moteConnector/graphs.html','w')

        stats = ""

        for r in res:
            print("loop = {} {}".format(r[0], r[1]))
            stats+="""[{asn}, {pdr}],\n""".format(asn=r[0], pdr=r[1])

        message = """
        <html>
        <head>
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
              google.charts.load('current', {{'packages':['corechart']}});
              google.charts.setOnLoadCallback(drawChart);

              function drawChart() {{
                var data = google.visualization.arrayToDataTable([
                    ['ASN', 'PDR'],
                    {}
                ]);

                var options = {{
 					hAxis: {{
         				title: 'ASN'
        			}},
        			vAxis: {{
          				title: 'PDR Rate'
       			 	}},
                  	title: 'Evolution of PDR',
                  	curveType: 'function',
                  	legend: {{ position: 'bottom' }}
                }};

                var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

                chart.draw(data, options);
              }}
            </script>
          </head>
            <body>
                <div id="curve_chart" style="width: 900px; height: 500px"></div>
            </body>
        </html>
              """.format(stats)

        f.write(message)
        f.close()

    def e2e(self):
        self.dbo.cur.execute("SELECT * FROM E2E WHERE expid={}".format(self.expid))
        self.dbo.db.commit()
        res = self.dbo.cur.fetchall()

        f = open('./openvisualizer/moteConnector/graphs.html','w')

        stats = ""

        for r in res:
            print("loop = {} {}".format(r[0], r[1]))
            stats+="""[{asn}, {pdr}],\n""".format(asn=r[0], pdr=r[1])

        message = """
        <html>
        <head>
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
              google.charts.load('current', {{'packages':['corechart']}});
              google.charts.setOnLoadCallback(drawChart);

              function drawChart() {{
                var data = google.visualization.arrayToDataTable([
                    ['ASN', 'PDR'],
                    {}
                ]);

                var options = {{
 					hAxis: {{
         				title: 'ASN'
        			}},
        			vAxis: {{
          				title: 'PDR Rate'
       			 	}},
                  	title: 'Evolution of PDR',
                  	curveType: 'function',
                  	legend: {{ position: 'bottom' }}
                }};

                var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

                chart.draw(data, options);
              }}
            </script>
          </head>
            <body>
                <div id="curve_chart" style="width: 900px; height: 500px"></div>
            </body>
        </html>
              """.format(stats)

        f.write(message)
        f.close()
