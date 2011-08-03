# -*- coding: utf-8 -*-

content='''
<html>
	<head>
		<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
		<title>AdLib rapportage</title>
        <style type='text/css'>
            table.rpt tr td.fieldname {
                background: #ddd;
            }
            table.rpt tr.q-complete {
                background: #afa;
            }
            table.rpt tr.q-almost-complete {
                background: #dfd;
            }
            table.rpt tr.multi-value td.valuesperdoc {
                background: #aaf;
            }
            table.rpt tr.invulboek td.fieldname {
                font-weight: bold;
            }
            div.tooltip {
                border: 1px solid black;
                background: #fff;
            }
            
            %INSERT_BLUEDREAM_CSS%
            
            .sortable th {
            	cursor: pointer;
            }
        </style>
        <script type='text/javascript'>
        	%INSERT_JQUERY_AND_TOOLTIP%
        </script>
        <script type='text/javascript'>
        	%INSERT_SORTTABLE%
        </script>
    </head>
    <body>

<div style="float: right">

<a href="http://www.west-vlaanderen.be/genieten/Cultuur/erfgoed/Pages/default.aspx" target="_blank"><img src="data:image/png;base64,%INSERT_WEST_VLAANDEREN_LOGO%" width="150" height="67" alt="Provincie West-Vlaanderen logo" border="0" /></a></div>

<a href="http://www.digiridoo.be/" target="_blank"><img src="data:image/png;base64,%INSERT_DIGIRIDOO_LOGO%" width="143" height="59" alt="Digiridoo logo" style="padding:10px 20px 10px 0px; border: none;" /></a>
'''