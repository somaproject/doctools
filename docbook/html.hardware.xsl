<?xml version='1.0'?> 
<xsl:stylesheet  
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"> 

<xsl:param name="graphic.default.extension">gif</xsl:param>

<xsl:include href="/usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl"/> 
<!-- IMAGE STUFF -->

<xsl:template name="mediaobject.filename">
  <xsl:param name="object"></xsl:param>

  <xsl:variable name="data" select="$object/videodata
                                    |$object/imagedata
                                    |$object/audiodata
                                    |$object"/>

  <xsl:variable name="filename">
    <xsl:choose>
      <xsl:when test="$data[@fileref]">
        <xsl:value-of select="$data/@fileref"/>
      </xsl:when>
      <xsl:when test="$data[@entityref]">
        <xsl:value-of select="unparsed-entity-uri($data/@entityref)"/>
      </xsl:when>
      <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="real.ext">
    <xsl:call-template name="filename-extension">
      <xsl:with-param name="filename" select="$filename"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="ext">
    <xsl:choose>
      <xsl:when test="$real.ext != ''">
        <xsl:value-of select="$real.ext"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$graphic.default.extension"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="graphic.ext">
    <xsl:call-template name="is.graphic.extension">
      <xsl:with-param name="ext" select="$ext"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="$real.ext = ''">
      <xsl:choose>
        <xsl:when test="$ext != ''">
          <xsl:value-of select="$filename"/>
          <xsl:text>.</xsl:text>
          <xsl:value-of select="$ext"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$filename"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="not($graphic.ext)">
      <xsl:choose>
        <xsl:when test="$graphic.default.extension != ''">
          <xsl:value-of select="$filename"/>
          <xsl:text>.</xsl:text>
          <xsl:value-of select="$graphic.default.extension"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$filename"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <!-- here's where we do our custom code -->
      <xsl:value-of select="concat(concat('objs/', $filename), '.png')"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<!-- TIMINGOBJECT MANIPULATIONS ==============================================

    Here we turn the timingobject into an img src=name.timing.svg, which obviously we would have had to have generated externally

-->

<xsl:template match="mediaobject|mediaobjectco">
  <xsl:variable name="olist" select="imageobject|imageobjectco
                     |videoobject|audioobject
                     |textobject|timingobject"/>

  <xsl:variable name="object.index">
    <xsl:call-template name="select.mediaobject.index">
      <xsl:with-param name="olist" select="$olist"/>
      <xsl:with-param name="count" select="1"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="object" select="$olist[position() = $object.index]"/>

  <xsl:variable name="align">
    <xsl:value-of select="$object/imagedata[@align][1]/@align"/>
  </xsl:variable>

  <div class="{name(.)}">
    <xsl:if test="$align != '' ">
      <xsl:attribute name="align">
        <xsl:value-of select="$align"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="@id">
      <a name="{@id}"/>
    </xsl:if>

    <xsl:apply-templates select="$object"/>
    <xsl:apply-templates select="caption"/>
  </div>
</xsl:template>



<xsl:template match="timingobject">
  <img> 
        <xsl:attribute name="src">img/<xsl:value-of select="@name"/>.timing.png</xsl:attribute>
  </img>
</xsl:template>

<!-- SIGNAL ================================================================


-->

<xsl:template match="signal">
  <b> 
    <xsl:choose>
      <xsl:when test="contains(., '[')">
	<xsl:value-of select="substring-before(., '[')"/>
	<sub>
	  <xsl:value-of select="substring-before(substring-after(., '['), ']')"/>
	</sub>
	
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="."/>
      </xsl:otherwise>
    </xsl:choose>
  </b>
</xsl:template>


</xsl:stylesheet>
