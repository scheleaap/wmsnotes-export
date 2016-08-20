<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="iso-8859-1" indent="yes"
		media-type="text/html" />
	<xsl:template match="/">
		<html>
			<head>
				<title>Notes</title>
				<link rel="stylesheet" href="style.css" type="text/css" />
				<link
					href="https://fonts.googleapis.com/css?family=Open+Sans:300,300italic,400,400italic,600,600italic,700,700italic,800,800italic"
					rel="stylesheet" type="text/css" />
			</head>
			<body>
				<div id="page">
					<div id="header">
						Recepten
					</div>
					<div id="content">
						<xsl:for-each select="/notes/note">
							<div class="note">
								<h1>
									<xsl:value-of select="@title" />
								</h1>
								<div class="info">
									<div class="path">
										<xsl:value-of select="path" />
									</div>
									<div class="description">
										<xsl:value-of select="description" />
									</div>
								</div>
								<div class="body">
									<xsl:copy-of select="body/*" />
								</div>
							</div>
						</xsl:for-each>
					</div>
				</div>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>