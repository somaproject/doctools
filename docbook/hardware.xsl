<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
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
  
  <xsl:template match="addr">
    <filename>
      <xsl:apply-templates select="@* | node()"/>
    </filename>
  </xsl:template>
  
  
  <xsl:template match="memmap">
    <informaltable frame="none">
      <title><xsl:value-of select="@title"/></title>
      <tgroup cols='2' align='left' colsep='1' rowsep='1'>
	<thead>
	  <row> 
	    <entry> Address </entry> 
	    <entry> Value</entry> 
	  </row>
	</thead>
	<tbody>
	  <xsl:apply-templates select="@* | node()"/>
	</tbody>
      </tgroup>
    </informaltable>
  </xsl:template>
  
  <xsl:template match="memmap/addr">
    <row>
      <entry>
	<filename>
	  <xsl:value-of select="@a"/>    
	</filename>
      </entry>
      <entry><para>     
	<xsl:apply-templates select="@* | node()"/>
      </para></entry>
    </row>
  </xsl:template>

  <xsl:template match="math">
    <![CDATA[$
	<xsl:apply-templates select="@* | node()"/>
     $]]>
  </xsl:template>
  
</xsl:stylesheet>
