<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                 >
 <xsl:template match="node()|@*">
   <xsl:copy>
   <xsl:apply-templates select="@*"/>
   <xsl:apply-templates/>
   </xsl:copy>
 </xsl:template>

<xsl:template match="signaldef">
   <variablelist>
     <xsl:apply-templates select="@* | node()"/>
   </variablelist>
</xsl:template>

<xsl:template match="signaldef/signal/name">
   <term>
     <xsl:apply-templates select="@* | node()"/>
   </term>
</xsl:template>

<xsl:template match="signaldef/signal">
  <varlistentry> <xsl:apply-templates select="@* | node()"/>
  </varlistentry>
</xsl:template>


<xsl:template match="signaldef/signal/info">
  <listitem><para>
    <xsl:apply-templates select="@* | node()"/>
  </para></listitem>
</xsl:template>


<xsl:template match="mediaobject/timingobject">
  <imageobject>
    <imagedata>
      <xsl:attribute name="fileref">
	<xsl:value-of select="@name"/>.timing.png</xsl:attribute>
    </imagedata>
  </imageobject>
</xsl:template>

</xsl:stylesheet>
