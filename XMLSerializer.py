# -*- coding: utf-8 -*-
import lxml.etree as ET

class Serializer(object):

    def __init__(self):
        return None
    @staticmethod
    def getSerializeMembers( SerializeObject):
        strSerializeMembers = []
        for member in dir(SerializeObject):
            strMember = str(member)
            strType = str(type(getattr(SerializeObject, strMember )))
            print( strMember + " : " + strType )
            if (strType.find("descriptor") == -1) and (strType.find("function") == -1) and (strType.find("method") ==-1) and (strMember.find("__") != 0):
                strSerializeMembers.append(strMember)
        print( "Serialize considered members : " + str(strSerializeMembers) )
        return strSerializeMembers
    @staticmethod
    def SerializeArray(XMLParent, arrayInst):
        for arrayIndex, arrayItem in enumerate(arrayInst):
            Serializer.SerializeMember(XMLParent, "elem" + str(arrayIndex), arrayItem )
    @staticmethod
    def SerializeMember(XMLParent, MemberName, newValue):
        strType = str(type(newValue))
        print( "serialize type : " + strType )
        if strType.find("instance") != -1:
            XMLParent = ET.SubElement(XMLParent, MemberName)
            Serializer.SerializeClass(newValue, XMLParent )
        elif strType.find("list") != -1:
            newElem = ET.SubElement(XMLParent, MemberName)
            Serializer.SerializeArray(newElem, newValue )
        else:
            newElem = ET.SubElement(XMLParent, MemberName)
            newElem.text = str(newValue)
    @staticmethod
    def SerializeClass(SerializeObject, rootElem = None):
        strSerMemberNames = Serializer.getSerializeMembers(SerializeObject)
        for strElem in strSerMemberNames:
            Serializer.SerializeMember( rootElem, strElem, getattr(SerializeObject, strElem ) )
    @staticmethod
    def Serialize(SerializeObject):
        strClassName = SerializeObject.__class__.__name__
        rootElem = ET.Element( strClassName )
        Serializer.SerializeClass(SerializeObject, rootElem)
        return ET.tostring(rootElem)

    @staticmethod
    def read(fileName, SerializeObject):
        root = ET.parse(fileName)
        return Serializer.DeserializeClass(SerializeObject, root.getroot())

    @staticmethod
    def write(fileName, SerializeObject):
        strClassName = SerializeObject.__class__.__name__
        rootElem = ET.Element( strClassName )
        Serializer.SerializeClass(SerializeObject, rootElem)
        ET.ElementTree(rootElem).write( fileName )

    @staticmethod
    def DeserializeArray(XMLParent, value):
        #array needs to have at least one value for correct type information, else values are read and treated as string
        theType = str
        if len(value) > 0:
            theType = type(value[0])
        arrayInst = []
        for arrayIndex, arrayNode in enumerate(XMLParent):
            arrayInst.append( Serializer.DeserializeMember( arrayNode, value[0] ) )
        return arrayInst
    @staticmethod
    def DeserializeMember(XMLElem, value ):
        theType = type(value)
        strType = str(theType)
        print( "Deserializing : " + strType )
        if strType.find("instance") != -1:
            return Serializer.DeserializeClass( value, XMLElem )
        elif strType.find("list") != -1:
            return  Serializer.DeserializeArray( XMLElem, value )
        else:
            return theType(XMLElem.text)
    @staticmethod
    def DeserializeClass(SerializeObject, rootElem):
        strSerMemberNames = Serializer.getSerializeMembers(SerializeObject)
        for strElem, xmlChildElem in zip(strSerMemberNames, rootElem):
            print("Deserializing : " +  strElem + " : ")
            print(str(xmlChildElem.text) )
            setattr(SerializeObject, strElem, Serializer.DeserializeMember(xmlChildElem, getattr(SerializeObject, strElem ) ) )
        return SerializeObject
    @staticmethod
    def DeSerialize(strXmlString, SerializeObject):
        strClassName = SerializeObject.__str__()
        print( "className : " + strClassName )
        root = ET.fromstring(strXmlString)
        return Serializer.DeserializeClass(SerializeObject, root)