import ast as StringConverter
from Includesfile import *
from xml.dom import minidom
import os 

#Prep the XML / vsysvar file for writting
root = minidom.Document()
  
xml = root.createElement('systemvariables') 
xml.setAttribute('version','4')
root.appendChild(xml)
  
OuterNameSpace = root.createElement('namespace')
OuterNameSpace.setAttribute('name', '')
OuterNameSpace.setAttribute('comment', '')
OuterNameSpace.setAttribute('interface', '')  
xml.appendChild(OuterNameSpace)


writerfile = open(OutputFileName, "w")

with open(DBCFileName) as f:
    lines = f.readline()
    while lines:
        if(lines.find(MessageNameFinder) == 0):
            EncoutneredNewMessage = 1
            MessageIDandNameString = lines.rpartition(':')[0]
            MessageNameSplitPosition = MessageIDandNameString.rfind(" ")
            MessageName = MessageIDandNameString[MessageNameSplitPosition + 1:]
            MessageID = MessageIDandNameString[4:MessageNameSplitPosition]                      #Find Message Name and Message ID in DBC

            
            
        elif(lines.find(SignalNameFinder) == 1):                                                #Find Signal name in DBC
            SignalNamewithSG_ = lines.rpartition(':')[0]
            SignalName = SignalNamewithSG_[5:-1]

            #This section of the code evaluates the  data type of the sysvar 
            Factor = lines[lines.find('(') + 1:lines.find(',')]                                 #Use the Factor of a signal from the DBC to determine if the signal should be represented by a float Sysvar
            if(isinstance(StringConverter.literal_eval(Factor),float)):
                SignalDataType = 'float'
            else:
                SignalDataType = 'int'
            # print(SignalName + '  Data type is - ' + SignalDataType)                          #Debug Line for String Converter library.

            #This section of the code evaluates the  bitcount of the sysvar 
            DLC = lines[lines.find('|') + 1:lines.find('@')]
            BitCount = '32'                                                                     #Default Bitcount = 32. Change to 64 only if DLC is high or if the data type is float.
            if(SignalDataType == 'float' or StringConverter.literal_eval(DLC) >= 32):
                BitCount = '64'
            
            #This section of the code evaluates whether the sysvar should be signed
            Offset = lines[lines.find(',') + 1:lines.find(')')]
            Issigned = 'false'                                                                  #By Default a sysvar is not signed. If the Offset is negative, then we consider it to be signed
            if(StringConverter.literal_eval(Offset) < 0):
                Issigned = 'true'
            #print(SignalName + '  Data type is - ' + SignalDataType + '\tBitcount is ' + BitCount + '\tIs Signed = ' + Issigned)    #Debug Line for String Converter library.

            #If The data type of a signal is int, Search if Value table Exists
            if(SignalDataType == 'int'):
                with open(DBCFileName) as Secondcopy:
                    
                    print("Find")
            
            if((lines.find(NodeName) >= 0) and EncoutneredNewMessage == 1):                     #If New message is found which is recieved by the PSCM, create name space for message
                writerfile.write(MessageName + "\n")
                EncoutneredNewMessage = 0
                CycleTime = '0'
                print(MessageName)

                #This Section of code finds the cycle time of the message.
                with open(DBCFileName) as Secondcopy:                                           
                    CycleTimerFinderPrefixStringformessage = CycleTimerFinderPrefixString + MessageID + ' '     #Open second copy of the dbc file to find the DBC defined Cycle time. 
                    CycleTimeIndex = CycleTimerFinderPrefixStringformessage.rfind(' ')
                    CycleTimeFinderLine = Secondcopy.readline()
                    while(CycleTimeFinderLine):                                                                 #Use the other instance of the file to parse through and find the cycle time of the particular message
                        if(CycleTimeFinderLine.find(CycleTimerFinderPrefixStringformessage) >= 0):
                            CycleTime = CycleTimeFinderLine[int(CycleTimeIndex) + 1:-2]
                            break
                        CycleTimeFinderLine = Secondcopy.readline()


                #Write Namespace as Message name                                                #Writes the message name as the Namespace
                NameSpaceMessageName = root.createElement('namespace')
                NameSpaceMessageName.setAttribute('name',MessageName)
                NameSpaceMessageName.setAttribute('comment', '')
                NameSpaceMessageName.setAttribute('interface', '')
                OuterNameSpace.appendChild(NameSpaceMessageName)
                
                #Create CycleTime Sysvar for every new message                                  #Creates a variable for cycle time
                SysVarSignalName = root.createElement('variable')
                SysVarSignalName.setAttribute('anlyzLocal','2')
                SysVarSignalName.setAttribute('readOnly','false')
                SysVarSignalName.setAttribute('valueSequence','false')
                SysVarSignalName.setAttribute('name','CycleTime')
                SysVarSignalName.setAttribute('startValue',CycleTime)
                SysVarSignalName.setAttribute('comment', '')
                SysVarSignalName.setAttribute('bitcount','32')
                SysVarSignalName.setAttribute('isSigned','false')
                SysVarSignalName.setAttribute('encoding','65001')
                SysVarSignalName.setAttribute('type','int')
                NameSpaceMessageName.appendChild(SysVarSignalName)


            if(lines.find(NodeName) >= 0):                                                      #If signal is recieved by PSCM, creates a sysvar for that signal
                writerfile.write("\t" + SignalName + "\n")

                #Write All signals into XML / Sysvar file
                SysVarSignalName = root.createElement('variable')
                SysVarSignalName.setAttribute('anlyzLocal','2')
                SysVarSignalName.setAttribute('readOnly','false')
                SysVarSignalName.setAttribute('valueSequence','false')
                SysVarSignalName.setAttribute('name',SignalName)
                SysVarSignalName.setAttribute('comment', '')
                SysVarSignalName.setAttribute('bitcount',BitCount)
                SysVarSignalName.setAttribute('isSigned',Issigned)
                SysVarSignalName.setAttribute('encoding','65001')
                SysVarSignalName.setAttribute('type',SignalDataType)
                NameSpaceMessageName.appendChild(SysVarSignalName)

        # print(Messagefound)
        lines = f.readline()
xml_str = root.toprettyxml(indent ="\t")                                                        #Indent XML file object

  
with open(sysvar_path_file, "w") as OutputSysvarFile:                                           #Actually create the XML file
    OutputSysvarFile.write(xml_str) 
writerfile.close()                                                                              #Close XML file