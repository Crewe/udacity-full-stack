#!/usr/bin/env python
#
# report.py - Reporting class for generating tournament stats


class TournamentReport(object):
    """A simple class to report on tournaments"""

    report_header = """<HTML>
<head>
    <style type="text/css">
    .matchup {
        display: inline-block;
        float: left;
    }
    .player {
        width:150px;
        height: 20px;
        display: inline-block;
        padding: 2px 5px;
    }

    .win {
        border-top: 1px solid black;
        border-right: 1px solid black;
        border-bottom: 1px solid black;
        display:inline-block;
        margin: 12px 0px auto 0px;
        width: inherit;
        text-align: right;
        vertical-align: middle;
        height: inherit;
        position:fixed;
        font-weight: bold;
    }
    .p-top {
        background-color: #aaa;
        border-top: 1px solid black;
        border-right: 1px solid black;
    }
    .p-bot {
        border-right: 1px solid black;
        border-bottom: 1px solid black;
    }

    .m-id {
        line-height:40px;
        padding: 4px;
        width:40px;
        height:40px;
        vertical-align: middle;
        display:inline-block;
        font-weight: bold;
        float:left;
        text-align:center;
        border:1px solid black;
    }

    .bolded { font-weight: bold; }

    .round {
        display:inline-block;
        width: 250px;
        float: left;
        padding-bottom: 30px;
    }

    table.results {
    border-width: 0px;
    border-spacing: 0px;
    border-style: none;
    border-color: gray;
    border-collapse: collapse;
    background-color: white;
}
table.results th {
    border-width: 1px;
    padding: 4px;
    border-style: solid;
    border-color: gray;
    background-color: white;
    -moz-border-radius: ;
}
table.results td {
    border-width: 1px;
    padding: 4px;
    border-style: solid;
    border-color: gray;
    background-color: white;
    -moz-border-radius: ;
}
    </style>
</head>
<body>
"""

    footer = "</body></HTML>"

    def __init__(self, filename="temp"):
        self.file_name = filename
        self.match_count = 1
        self.player_data = "<h2>Players</h2>"
        self.matches = {}
        self.match_data = "<h2>Matches</h2>"
        self.result_data = "<h2>Results</h2>"
        self.event_name = "<h1>" + filename + " Results</h1>"
        self.round = 1

    def setRound(self, rnd):
        self.round = rnd + 1

    def filename(self, name):
        self.file_name = name + ".html"

    def eventName(self, name):
        self.event_name = "<h1>" + name + " Results</h1>"

    def addPlayerList(self, players):
        self.player_data += "<ol>"
        for p in players:
            self.player_data += "<li>" + p + "</li>"
        self.player_data += "</ol>"

    def clearReport(self):
        self.__init__()

    def addMatchResult(self, p1, p2, winner):
        m = """
        <div class="m-id">
            {0}{1}
        </div>
        <div class="matchup">
            <div class="player p-top {bolda}">{2}</div><br/>
            <div class="player p-bot {boldb}">{3}</div>
        </div>
        <!--
        <div class="win">
            <div class="player">{4}</div>
        </div> -->
""".format(self.round, self.match_count, p1, p2, winner,
           bolda="bolded" if p1 == winner else "",
           boldb="bolded" if p2 == winner else "")
        if str(self.round) in self.matches:
            self.matches[str(self.round)] += m
        else:
            self.matches[str(self.round)] = m
        self.match_count += 1

    def addFinalResults(self, data):
        self.result_data += """
        <h3>Round {0}</h3>
        <table class="results"><tr>
        <th>Place</th><th>Name</th><th>Wins</th><th>Matches</th>
        </tr>
        """.format(self.round)
        x = 1
        for p in data:
            self.result_data += """
            <tr><td>{0}.</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>
            """.format(x, p[1], p[2], p[3])
            x += 1
        self.result_data += "</table><br/>"

    def writeReport(self):
        self.match_data += '<div style="display: inline-block;">'
        for key in range(len(self.matches)):
            m = '<div class="round">{0}</div>'.format(self.matches[str(key + 1)])
            self.match_data += m
        self.match_data += "</div>"
        self.file = open(self.file_name, 'w')
        self.file.write(self.report_header + self.event_name +
                        self.player_data + self.match_data +
                        self.result_data + self.footer)
        self.file.close()
